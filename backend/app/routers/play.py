import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import chess
import chess.engine

from app.core.config import find_stockfish
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.ratelimit import rate_limit
from app.models.chess import User, BadMove

router = APIRouter(prefix="/play", tags=["play"])

ANGRY_MESSAGES = [
    "😠 You did that AGAIN?! We've talked about this...",
    "😤 Are you even reading my advice? This is your {counter}th time!",
    "🤬 SERIOUSLY? Same mistake {counter} times now. I'm losing my mind!",
    "😡 I'm this close to resigning from being your coach!",
    "🔨 THAT'S IT. Go review your mistakes right now!",
    "💢 Unbelievable. You've done this {counter} times now.",
]

NORMAL_MESSAGES = [
    "Hmm, that could be better. Let's review it.",
    "Not the best choice. Care to try another path?",
    "That's a mistake. The book move is better here.",
    "Careful! That move leaves you vulnerable.",
]

GOOD_MESSAGES = [
    "✅ Nice move!",
    "👍 Good choice.",
    "👏 Well played.",
    "😊 That's the way!",
]


class PlayMoveRequest(BaseModel):
    fen: str  # FEN after the player's move
    fen_before: str  # FEN before the player's move


class PlayMoveResponse(BaseModel):
    evaluation: float
    best_move: str | None
    uci_move: str | None
    stockfish_move: str | None
    stockfish_uci: str | None
    is_mistake: bool
    mistake_level: str | None
    repeated_mistake: bool
    repeated_count: int
    message: str


def classify_eval_drop(eval_diff: float) -> tuple[bool, str | None]:
    """Classify how bad an evaluation drop was. Returns (is_mistake, mistake_level)."""
    if eval_diff <= -2.5:
        return True, "blunder"
    if eval_diff <= -1.0:
        return True, "mistake"
    if eval_diff <= -0.5:
        return True, "inaccuracy"
    return False, None


def _evaluate_after_player_move(fen_before: str, fen: str) -> dict:
    """Run the blocking Stockfish analysis (call via asyncio.to_thread)."""
    path = find_stockfish()
    if not path:
        raise RuntimeError("Stockfish engine not found. Set STOCKFISH_PATH.")

    board_before = chess.Board(fen_before)
    board_after = chess.Board(fen)

    engine = chess.engine.SimpleEngine.popen_uci(path)
    try:
        # Analyze position before the player's move
        result = engine.analyse(board_before, chess.engine.Limit(depth=12))
        eval_before = result["score"].pov(chess.WHITE).score(mate_score=10000) / 100.0
        best_move = result.get("pv", [None])[0]
        best_move_san = board_before.san(best_move) if best_move else "N/A"
        best_move_uci = best_move.uci() if best_move else None

        # Analyze position after the player's move (Stockfish's turn)
        result_after = engine.analyse(board_after, chess.engine.Limit(depth=12))
        eval_after = result_after["score"].pov(chess.WHITE).score(mate_score=10000) / 100.0

        player_just_moved = "black" if board_after.turn == chess.WHITE else "white"
        eval_diff = (eval_after - eval_before) if player_just_moved == "white" else -(eval_after - eval_before)

        is_mistake, mistake_level = classify_eval_drop(eval_diff)

        # Stockfish's reply: best move from the position AFTER the player's move
        best_reply = result_after.get("pv", [None])[0]
        sf_move = board_after.san(best_reply) if best_reply else None
        sf_uci = best_reply.uci() if best_reply else None

        return {
            "eval_after": eval_after,
            "best_move_san": best_move_san,
            "best_move_uci": best_move_uci,
            "sf_move": sf_move,
            "sf_uci": sf_uci,
            "is_mistake": is_mistake,
            "mistake_level": mistake_level,
        }
    finally:
        engine.quit()


@router.post("/move", response_model=PlayMoveResponse)
async def play_move(
    request: PlayMoveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(30, 60)),
):
    """Evaluate the player's move and detect repeated mistakes."""
    try:
        # Validate FENs (build boards to ensure they parse)
        chess.Board(request.fen_before)
        chess.Board(request.fen)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid FEN")

    try:
        # Blocking engine analysis runs in a worker thread (keeps the event loop free)
        a = await asyncio.to_thread(_evaluate_after_player_move, request.fen_before, request.fen)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    # Check for repeated mistake: same resulting FEN in bad_moves history
    match_result = await db.execute(
        select(BadMove).where(
            BadMove.user_id == current_user.id,
            BadMove.fen == chess.Board(request.fen).fen(),
        )
    )
    matching = match_result.scalars().all()
    repeated_mistake = bool(matching)
    repeated_count = max(m.counter for m in matching) if matching else 0

    # Build message
    if repeated_mistake and a["is_mistake"]:
        idx = min(max(repeated_count - 1, 0), len(ANGRY_MESSAGES) - 1)
        message = ANGRY_MESSAGES[idx].replace("{counter}", str(repeated_count))
    elif a["is_mistake"]:
        idx = min(max(repeated_count, 0), len(NORMAL_MESSAGES) - 1)
        message = NORMAL_MESSAGES[idx]
    else:
        message = GOOD_MESSAGES[0]

    return PlayMoveResponse(
        evaluation=a["eval_after"],
        best_move=a["best_move_san"],
        uci_move=a["best_move_uci"],
        stockfish_move=a["sf_move"],
        stockfish_uci=a["sf_uci"],
        is_mistake=a["is_mistake"],
        mistake_level=a["mistake_level"],
        repeated_mistake=repeated_mistake,
        repeated_count=repeated_count,
        message=message,
    )