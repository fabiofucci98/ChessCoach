import httpx
from datetime import datetime, timedelta
from typing import Optional

CHESS_COM_API_BASE = "https://api.chess.com/pub"


async def fetch_user_games(username: str, months_back: int = 1, limit: int = 100) -> list[dict]:
    """
    Fetch recent games for a chess.com user.

    The chess.com API provides games by month. We fetch the current month
    and optionally the previous month to get recent games.
    """
    games = []
    now = datetime.utcnow()

    for i in range(months_back):
        month_date = now - timedelta(days=30 * i)
        year = month_date.year
        month = month_date.month

        url = f"{CHESS_COM_API_BASE}/player/{username}/games/{year}/{month:02d}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)

            if response.status_code == 404:
                # No games for this month
                continue

            response.raise_for_status()
            data = response.json()
            month_games = data.get("games", [])
            # Sort by end_time descending (most recent first)
            month_games.sort(key=lambda g: g.get("end_time", 0), reverse=True)
            games.extend(month_games)

    # Sort all games by end_time descending and limit
    games.sort(key=lambda g: g.get("end_time", 0), reverse=True)
    return games[:limit]


async def fetch_user_profile(username: str) -> Optional[dict]:
    """Fetch a chess.com user profile."""
    url = f"{CHESS_COM_API_BASE}/player/{username}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()