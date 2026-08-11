import uuid
import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, UUID4
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.ratelimit import rate_limit
from app.models.chess import User, Game, BadMove
from app.services.chess_com import fetch_user_games, fetch_user_profile
from app.routers.analysis import analyze_game_moves, upsert_bad_moves

router = APIRouter(prefix="/games", tags=["games"])

# In-memory sync progress tracker (per user_id)
_sync_progress: dict[str, dict] = {}
_sync_tasks: dict[str, asyncio.Task] = {}


class GameResponse(BaseModel):
    id: UUID4
    external_game_id: str
    time_control: str | None
    player_color: str
    user_rating: int | None
    opponent_rating: int | None
    result: str | None
    is_analyzed: bool
    played_at: datetime | None
    pgn: str

    class Config:
        from_attributes = True


class SyncResponse(BaseModel):
    synced: int
    new_games: int
    games: list[GameResponse]


class SyncStatusResponse(BaseModel):
    running: bool
    progress: int
    current_game: int
    total_games: int
    message: str


def parse_chess_com_game(game_data: dict, username: str) -> dict:
    """Parse a chess.com game dict into our Game model fields."""
    white = game_data.get("white", {})
    black = game_data.get("black", {})

    white_username = white.get("username", "").lower()
    username_lower = username.lower()

    if white_username == username_lower:
        player_color = "white"
        user_rating = white.get("rating")
        opponent_rating = black.get("rating")
    else:
        player_color = "black"
        user_rating = black.get("rating")
        opponent_rating = white.get("rating")

    # Determine result from the player's perspective
    player_result = white.get("result", "") if player_color == "white" else black.get("result", "")

    if player_result in ("win",):
        result = "win"
    elif player_result in ("checkmated", "timeout", "resigned", "abandoned", "bughousepartnerlose"):
        result = "loss"
    elif player_result in ("agreed", "repetition", "stalemate", "insufficient", "50move", "timevsinsufficient"):
        result = "draw"
    else:
        result = "loss"

    # Parse played_at from timestamp
    played_at = None
    end_time = game_data.get("end_time")
    if end_time:
        played_at = datetime.fromtimestamp(end_time)

    return {
        "external_game_id": game_data.get("uuid", ""),
        "pgn": game_data.get("pgn", ""),
        "time_control": game_data.get("time_control"),
        "player_color": player_color,
        "user_rating": user_rating,
        "opponent_rating": opponent_rating,
        "result": result,
        "played_at": played_at,
    }


async def _run_sync(user_id: uuid.UUID, username: str, sync_limit: int, db: AsyncSession):
    """Background sync task: fetch games, analyze one at a time, commit after each."""
    user_key = str(user_id)
    try:
        # Fetch games from chess.com
        _sync_progress[user_key] = {"running": True, "progress": 5, "current_game": 0, "total_games": 0, "message": "Fetching games from chess.com..."}
        chess_com_games = await fetch_user_games(username, months_back=6, limit=sync_limit)
        _sync_progress[user_key]["total_games"] = len(chess_com_games)
        _sync_progress[user_key]["progress"] = 20
        _sync_progress[user_key]["message"] = f"Found {len(chess_com_games)} games"

        # Get existing game IDs to avoid duplicates
        result = await db.execute(
            select(Game.external_game_id).where(Game.user_id == user_id)
        )
        existing_ids = set(result.scalars().all())

        new_games = []
        for game_data in chess_com_games:
            external_id = game_data.get("uuid", "")
            if external_id in existing_ids:
                continue

            parsed = parse_chess_com_game(game_data, username)

            game = Game(
                user_id=user_id,
                platform="chess_com",
                **parsed,
            )
            db.add(game)
            new_games.append(game)

        await db.commit()

        # Auto-analyze new games one at a time, committing after each
        total_new = len(new_games)
        for idx, game in enumerate(new_games):
            await db.refresh(game)
            _sync_progress[user_key]["current_game"] = idx + 1
            _sync_progress[user_key]["progress"] = 20 + int(80 * (idx + 1) / max(total_new, 1))
            _sync_progress[user_key]["message"] = f"Analyzing game {idx + 1}/{total_new}..."

            # Blocking engine work runs in a worker thread (keeps the event loop free)
            bad_moves_data = await asyncio.to_thread(
                analyze_game_moves,
                pgn=game.pgn,
                player_color=game.player_color,
                user_id=user_id,
                game_id=game.id,
            )

            await upsert_bad_moves(db, user_id, bad_moves_data)

            game.is_analyzed = True
            # Commit after each game so mistakes appear incrementally
            await db.commit()

        _sync_progress[user_key] = {"running": False, "progress": 100, "current_game": total_new, "total_games": total_new, "message": "Sync complete"}
    except Exception as e:
        _sync_progress[user_key] = {"running": False, "progress": 0, "current_game": 0, "total_games": 0, "message": f"Sync failed: {str(e)}"}
    finally:
        _sync_tasks.pop(user_key, None)


@router.post("/sync", response_model=SyncResponse)
async def sync_games(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(5, 60)),
):
    """Start a background sync of games from chess.com for the current user."""
    if not current_user.chess_com_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please set your chess.com username first",
        )

    # Verify the chess.com user exists
    profile = await fetch_user_profile(current_user.chess_com_username)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chess.com user '{current_user.chess_com_username}' not found",
        )

    user_key = str(current_user.id)

    # If a sync is already running, don't start another
    if _sync_tasks.get(user_key) and not _sync_tasks[user_key].done():
        return SyncResponse(synced=0, new_games=0, games=[])

    # Start background sync task
    task = asyncio.create_task(_run_sync(current_user.id, current_user.chess_com_username, current_user.sync_limit, db))
    _sync_tasks[user_key] = task

    return SyncResponse(synced=0, new_games=0, games=[])


@router.get("/sync/status", response_model=SyncStatusResponse)
async def get_sync_status(
    current_user: User = Depends(get_current_user),
):
    """Get the current sync progress for the user."""
    status_data = _sync_progress.get(str(current_user.id), {"running": False, "progress": 0, "current_game": 0, "total_games": 0, "message": "No sync in progress"})
    return SyncStatusResponse(**status_data)


@router.get("", response_model=list[GameResponse])
async def list_games(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List the user's analyzed games, most recent first."""
    result = await db.execute(
        select(Game)
        .where(Game.user_id == current_user.id, Game.is_analyzed == True)
        .order_by(desc(Game.played_at))
        .limit(limit)
    )
    games = result.scalars().all()

    return [GameResponse.model_validate(g) for g in games]


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific game by ID."""
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

    return GameResponse.model_validate(game)