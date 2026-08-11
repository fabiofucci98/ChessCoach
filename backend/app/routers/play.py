import os

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import chess
import chess.engine

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.chess import User, BadMove

router = APIRouter(prefix="/play", tags=["play"])

STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")

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


@router.post("/move", response_model=PlayMoveResponse)
async def play_move(
    request: PlayMoveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Evaluate the player's move and detect repeated mistakes."""
    try:
        board_before = chess.Board(request.fen_before)
        board_after = chess.Board(request.fen)
    except Exception:
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid FEN")

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

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

        # The player who just moved is the one NOT to move now
        player_just_moved = "black" if board_after.turn == chess.WHITE else "white"

        if player_just_moved == "white":
            eval_diff = eval_after - eval_before
        else:
            eval_diff = -(eval_after - eval_before)

        is_mistake = False
        mistake_level = None
        if eval_diff <= -2.5:
            is_mistake = True
            mistake_level = "blunder"
        elif eval_diff <= -1.0:
            is_mistake = True
            mistake_level = "mistake"
        elif eval_diff <= -0.5:
            is_mistake = True
            mistake_level = "inaccuracy"

        # Check for repeated mistake: same resulting FEN in bad_moves history
        repeated_mistake = False
        repeated_count = 0
        match_result = await db.execute(
            select(BadMove).where(
                BadMove.user_id == current_user.id,
                BadMove.fen == board_after.fen(),
            )
        )
        matching = match_result.scalars().all()
        if matching:
            repeated_mistake = True
            repeated_count = max(m.counter for m in matching)

        # Build message
        if repeated_mistake and is_mistake:
            idx = min(max(repeated_count - 1, 0), len(ANGRY_MESSAGES) - 1)
            message = ANGRY_MESSAGES[idx].replace("{counter}", str(repeated_count))
        elif is_mistake:
            idx = min(max(repeated_count, 0), len(NORMAL_MESSAGES) - 1)
            message = NORMAL_MESSAGES[idx]
        else:
            message = GOOD_MESSAGES[0]

        # Stockfish's reply move (best move from the position after player's move)
        sf_move = None
        sf_uci = None
        if best_move_uci:
            sf_move = best_move_san
            sf_uci = best_move_uci

        return PlayMoveResponse(
            evaluation=eval_after,
            best_move=best_move_san,
            uci_move=best_move_uci,
            stockfish_move=sf_move,
            stockfish_uci=sf_uci,
            is_mistake=is_mistake,
            mistake_level=mistake_level,
            repeated_mistake=repeated_mistake,
            repeated_count=repeated_count,
            message=message,
        )

    finally:
        engine.quit()