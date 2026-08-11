import asyncio
import os
import platform

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.config import find_stockfish, settings
from app.core.ratelimit import rate_limit
from app.core.stockfish import analyze_position

load_dotenv()


app = FastAPI(
    title="ChessCoach API",
    version="0.1.0",
    description="Engine-powered personalized chess coaching backend."
)

# CORS origins come from settings (configurable via CORS_ORIGINS env var)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    fen: str


@app.post("/analyze")
async def analyze_position_endpoint(
    request: AnalysisRequest,
    _: None = Depends(rate_limit(15, 60)),
):
    # Run the blocking Stockfish analysis in a worker thread to keep the event loop free
    return await asyncio.to_thread(analyze_position, request.fen)


# Include routers
from app.routers import auth, games, analysis, play, puzzles

app.include_router(auth.router)
app.include_router(games.router)
app.include_router(analysis.router)
app.include_router(play.router)
app.include_router(puzzles.router)


@app.get("/")
async def root():
    return {
        "message": "ChessCoach API is running!"
    }


@app.get("/health")
async def health_check():
    stockfish_path = find_stockfish()
    return {
        "status": "healthy",
        "environment": platform.system(),
        "env_stockfish_path": os.getenv("STOCKFISH_PATH"),
        "stockfish": {
            "installed": stockfish_path is not None,
            "path": stockfish_path,
        },
    }
