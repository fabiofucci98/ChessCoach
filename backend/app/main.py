from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import platform
from pathlib import Path

load_dotenv()


app = FastAPI(
    title="ChessCoach API",
    version="0.1.0",
    description="Engine-powered personalized chess coaching backend."
)

# Enable CORS for Next.js app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    fen: str


from app.core.stockfish import analyze_position


@app.post("/analyze")
async def analyze_position_endpoint(
    request: AnalysisRequest
):

    result = analyze_position(
        request.fen
    )

    return result


# Include routers
from app.routers import auth, games, analysis, play, puzzles

app.include_router(auth.router)
app.include_router(games.router)
app.include_router(analysis.router)
app.include_router(play.router)
app.include_router(puzzles.router)




def find_stockfish():
    """
    Detect Stockfish installation depending on environment.

    Local development:
        - Uses STOCKFISH_PATH env variable if provided
        - Searches common Windows locations

    Docker/Linux:
        - Uses STOCKFISH_PATH env variable if provided
        - Searches PATH
        - Checks default Linux package location
    """

    # 1. Explicit override (recommended)
    env_path = os.getenv("STOCKFISH_PATH")

    if env_path and Path(env_path).exists():
        return env_path


    system = platform.system()

    # 2. Local Windows development
    if system == "Windows":
        windows_paths = [
            r"C:\Program Files\Stockfish\stockfish.exe",
            r"C:\Program Files (x86)\Stockfish\stockfish.exe",
            r"C:\stockfish\stockfish.exe",
        ]

        for path in windows_paths:
            if Path(path).exists():
                return path

        # Search PATH
        stockfish = shutil.which("stockfish")
        if stockfish:
            return stockfish


    # 3. Docker/Linux environment
    else:
        linux_paths = [
            "/usr/games/stockfish",
            "/usr/bin/stockfish",
        ]

        for path in linux_paths:
            if Path(path).exists():
                return path

        # Search PATH
        stockfish = shutil.which("stockfish")
        if stockfish:
            return stockfish


    return None


@app.get("/")
async def root():
    return {
        "message": "ChessCoach API is running!"
    }


@app.get("/health")
async def health_check():
    print("STOCKFISH_PATH =", os.getenv("STOCKFISH_PATH"))

    stockfish_path = find_stockfish()

    return {
        "status": "healthy",
        "environment": platform.system(),
        "env_stockfish_path": os.getenv("STOCKFISH_PATH"),
        "stockfish": {
            "installed": stockfish_path is not None,
            "path": stockfish_path
        }
    }