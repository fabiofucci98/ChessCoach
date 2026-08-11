import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, UUID4
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import utcnow
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.chess import User, BadMove

router = APIRouter(prefix="/analysis/puzzles", tags=["puzzles"])


class PuzzleResponse(BaseModel):
    id: UUID4
    fen_before: str
    best_move: str
    move_played: str
    move_number: int
    counter: int
    evaluation_before: float
    evaluation_after: float
    repetitions: int
    interval: int
    next_review_at: datetime | None


class PuzzleAnswerRequest(BaseModel):
    move: str


class PuzzleAnswerResponse(BaseModel):
    correct: bool
    best_move: str
    move_played: str
    next_review_at: datetime
    repetitions: int
    interval: int


def sm2_update(easiness_factor: float, repetitions: int, interval: int, quality: int) -> tuple[float, int, int]:
    """SM-2 spaced repetition. quality: 0-5 (0=wrong, 5=perfect)."""
    if quality < 3:
        return easiness_factor, 0, 1

    if repetitions == 0:
        interval = 1
    elif repetitions == 1:
        interval = 6
    else:
        interval = round(interval * easiness_factor)

    repetitions += 1
    ef = max(1.3, easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    return ef, repetitions, interval


@router.get("/next", response_model=PuzzleResponse | None)
async def get_next_puzzle(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the next puzzle due for review."""
    now = utcnow()

    # First: puzzles due for review
    result = await db.execute(
        select(BadMove)
        .where(
            BadMove.user_id == current_user.id,
            BadMove.next_review_at.isnot(None),
            BadMove.next_review_at <= now,
        )
        .order_by(BadMove.next_review_at)
        .limit(1)
    )
    puzzle = result.scalar_one_or_none()

    if puzzle is None:
        # No due puzzles: pick most frequent mistake not yet reviewed
        result = await db.execute(
            select(BadMove)
            .where(
                BadMove.user_id == current_user.id,
                BadMove.next_review_at.is_(None),
            )
            .order_by(desc(BadMove.counter))
            .limit(1)
        )
        puzzle = result.scalar_one_or_none()

    if puzzle is None:
        return None

    return PuzzleResponse(
        id=puzzle.id,
        fen_before=puzzle.fen_before or puzzle.fen,
        best_move=puzzle.best_move,
        move_played=puzzle.move_played,
        move_number=puzzle.move_number,
        counter=puzzle.counter,
        evaluation_before=puzzle.evaluation_before,
        evaluation_after=puzzle.evaluation_after,
        repetitions=puzzle.repetitions,
        interval=puzzle.interval,
        next_review_at=puzzle.next_review_at,
    )


@router.post("/{puzzle_id}/answer", response_model=PuzzleAnswerResponse)
async def answer_puzzle(
    puzzle_id: uuid.UUID,
    request: PuzzleAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Answer a puzzle and update spaced repetition schedule."""
    result = await db.execute(
        select(BadMove).where(
            BadMove.id == puzzle_id,
            BadMove.user_id == current_user.id,
        )
    )
    puzzle = result.scalar_one_or_none()

    if puzzle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puzzle not found",
        )

    correct = request.move.strip().lower() == puzzle.best_move.strip().lower()
    quality = 5 if correct else 1
    ef, reps, interval = sm2_update(
        puzzle.easiness_factor,
        puzzle.repetitions,
        puzzle.interval,
        quality,
    )

    now = utcnow()
    puzzle.easiness_factor = ef
    puzzle.repetitions = reps
    puzzle.interval = interval
    puzzle.last_reviewed_at = now
    puzzle.next_review_at = now + timedelta(days=interval)

    await db.commit()
    await db.refresh(puzzle)

    return PuzzleAnswerResponse(
        correct=correct,
        best_move=puzzle.best_move,
        move_played=puzzle.move_played,
        next_review_at=puzzle.next_review_at,
        repetitions=puzzle.repetitions,
        interval=puzzle.interval,
    )