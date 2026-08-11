import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "ChessCoach"
    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "chesscoach")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "chesscoach_secret")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "chesscoach_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
