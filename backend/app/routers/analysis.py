import asyncio
import uuid
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, UUID4
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
import chess
import chess.engine
import chess.pgn

from app.core.config import find_stockfish
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.chess import User, Game, BadMove

router = APIRouter(prefix="/analysis", tags=["analysis"])


class BadMoveResponse(BaseModel):
    id: UUID4
    game_id: UUID4
    fen: str
    fen_before: str | None = None
    move_played: str
    best_move: str
    evaluation_before: float
    evaluation_after: float
    move_number: int
    counter: int
    easiness_factor: float = 2.5
    interval: int = 0
    repetitions: int = 0
    next_review_at: datetime | None = None
    last_reviewed_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyzeGameResponse(BaseModel):
    game_id: UUID4
    bad_moves_found: int
    bad_moves: list[BadMoveResponse]


class BadMovesSummaryResponse(BaseModel):
    total_bad_moves: int
    bad_moves: list[BadMoveResponse]


def analyze_game_moves(pgn: str, player_color: str, user_id: uuid.UUID, game_id: uuid.UUID) -> list[dict]:
    """
    Analyze all moves of a game using Stockfish to find bad moves.
    A bad move is one where the evaluation drops significantly (blunder/mistake).
    """
    board = chess.Board()

    # Load PGN
    try:
        pgn_io = chess.pgn.read_game(io.StringIO(pgn))
        if pgn_io is None:
            return []
    except Exception:
        return []

    # Get the moves
    moves = list(pgn_io.mainline_moves())
    if not moves:
        return []

    path = find_stockfish()
    if not path:
        raise RuntimeError("Stockfish engine not found. Set STOCKFISH_PATH.")
    engine = chess.engine.SimpleEngine.popen_uci(path)

    bad_moves_found = []

    try:
        for move_number, move in enumerate(moves, start=1):
            # Determine if this is the player's move BEFORE making it
            is_players_turn = (board.turn == chess.WHITE and player_color == "white") or \
                              (board.turn == chess.BLACK and player_color == "black")

            # Capture FEN before the move (for puzzle reconstruction)
            fen_before = board.fen()

            # Get evaluation BEFORE the move
            result = engine.analyse(board, chess.engine.Limit(depth=12))
            eval_before = result["score"].pov(chess.WHITE).score(mate_score=10000) / 100.0

            # Get the best move suggested by Stockfish at this position
            best_move = result.get("pv", [None])[0]

            # Get the SAN of the player's move BEFORE pushing (needed for logging)
            move_san = board.san(move)
            best_move_san = board.san(best_move) if best_move else "N/A"

            # Make the move
            board.push(move)

            # Get evaluation AFTER the move
            result = engine.analyse(board, chess.engine.Limit(depth=12))
            eval_after = result["score"].pov(chess.WHITE).score(mate_score=10000) / 100.0

            if not is_players_turn:
                continue

            # Calculate evaluation difference (how much the position worsened)
            if player_color == "white":
                eval_diff = eval_after - eval_before
            else:
                eval_diff = -(eval_after - eval_before)  # For black, negate because scores are from white's perspective

            # Threshold: if evaluation drops >= 0.5 pawns, it's a bad move
            if eval_diff <= -0.3:
                bad_moves_found.append({
                    "user_id": user_id,
                    "game_id": game_id,
                    "fen": board.fen(),
                    "fen_before": fen_before,
                    "move_played": move_san,
                    "best_move": best_move_san,
                    "evaluation_before": eval_before,
                    "evaluation_after": eval_after,
                    "move_number": move_number,
                    "counter": 1,
                })

    finally:
        engine.quit()

    return bad_moves_found


async def upsert_bad_moves(db: AsyncSession, user_id: uuid.UUID, bad_moves_data: list[dict]) -> list[BadMove]:
    """Save bad moves, incrementing the counter on duplicates (same user + FEN + move_played)."""
    objects = []
    for bm_data in bad_moves_data:
        existing_result = await db.execute(
            select(BadMove).where(
                BadMove.user_id == user_id,
                BadMove.fen == bm_data["fen"],
                BadMove.move_played == bm_data["move_played"],
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            existing.counter += 1
            objects.append(existing)
        else:
            bm = BadMove(**bm_data)
            db.add(bm)
            objects.append(bm)
    return objects


@router.post("/games/{game_id}", response_model=AnalyzeGameResponse)
async def analyze_game(
    game_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze a specific game and identify bad moves."""
    # Get the game
    result = await db.execute(
        select(Game).where(
            Game.id == game_id,
            Game.user_id == current_user.id,
        )
    )
    game = result.scalar_one_or_none()

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    # Run the blocking analysis in a worker thread (keeps the event loop free)
    try:
        bad_moves_data = await asyncio.to_thread(
            analyze_game_moves,
            pgn=game.pgn,
            player_color=game.player_color,
            user_id=current_user.id,
            game_id=game.id,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    # Save bad moves, deduping and incrementing counters
    bad_move_objects = await upsert_bad_moves(db, current_user.id, bad_moves_data)

    # Mark game as analyzed
    game.is_analyzed = True
    await db.commit()

    # Refresh all bad move objects
    for bm in bad_move_objects:
        await db.refresh(bm)

    return AnalyzeGameResponse(
        game_id=game.id,
        bad_moves_found=len(bad_move_objects),
        bad_moves=[BadMoveResponse.model_validate(bm) for bm in bad_move_objects],
    )


@router.get("/bad-moves", response_model=BadMovesSummaryResponse)
async def get_bad_moves(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all bad moves for the current user, most frequent first."""
    result = await db.execute(
        select(BadMove)
        .where(BadMove.user_id == current_user.id)
        .order_by(desc(BadMove.counter), desc(BadMove.created_at))
        .limit(limit)
    )
    bad_moves = result.scalars().all()

    return BadMovesSummaryResponse(
        total_bad_moves=len(bad_moves),
        bad_moves=[BadMoveResponse.model_validate(bm) for bm in bad_moves],
    )