import os
import platform
import shutil
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


def utcnow() -> datetime:
    """Return the current UTC time as a naive datetime (matches the DB's timestamp columns)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def find_stockfish() -> str | None:
    """Locate the Stockfish binary across environments (explicit path, OS defaults, PATH)."""
    # 1. Explicit override (recommended)
    env_path = os.getenv("STOCKFISH_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    system = platform.system()

    if system == "Windows":
        windows_paths = [
            r"C:\Program Files\Stockfish\stockfish.exe",
            r"C:\Program Files (x86)\Stockfish\stockfish.exe",
            r"C:\stockfish\stockfish.exe",
        ]
        for path in windows_paths:
            if Path(path).exists():
                return path
    else:
        linux_paths = ["/usr/games/stockfish", "/usr/bin/stockfish"]
        for path in linux_paths:
            if Path(path).exists():
                return path

    return shutil.which("stockfish")


class Settings(BaseSettings):
    PROJECT_NAME: str = "ChessCoach"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "chesscoach")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "chesscoach_secret")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "chesscoach_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "chesscoach-dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Comma-separated list of allowed CORS origins
    # e.g. "http://localhost:3000,https://app.example.com"
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if o.strip()
    ]

    # Log every SQL statement when true
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "false").lower() in ("1", "true", "yes", "on")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()

# Fail fast in production if the secret key is missing or the insecure dev default
if settings.ENVIRONMENT == "production":
    if not settings.SECRET_KEY or settings.SECRET_KEY == "chesscoach-dev-secret-key-change-in-production":
        raise RuntimeError("SECRET_KEY must be set to a secure value in production")
