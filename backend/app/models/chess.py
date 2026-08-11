import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from app.core.config import utcnow

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    chess_com_username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sync_limit: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    games = relationship("Game", back_populates="user", cascade="all, delete-orphan")
    bad_moves = relationship("BadMove", back_populates="user", cascade="all, delete-orphan")


class Game(Base):
    __tablename__ = "games"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    platform: Mapped[str] = mapped_column(String(20), default="chess_com")
    external_game_id: Mapped[str] = mapped_column(String(100), nullable=False)
    pgn: Mapped[str] = mapped_column(Text, nullable=False)
    time_control: Mapped[str | None] = mapped_column(String(50), nullable=True)
    player_color: Mapped[str] = mapped_column(String(10), nullable=False)
    user_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    opponent_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_analyzed: Mapped[bool] = mapped_column(Boolean, default=False)
    played_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="games")
    bad_moves = relationship("BadMove", back_populates="game", cascade="all, delete-orphan")


class BadMove(Base):
    __tablename__ = "bad_moves"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    game_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("games.id", ondelete="CASCADE"))
    fen: Mapped[str] = mapped_column(Text, nullable=False)
    fen_before: Mapped[str | None] = mapped_column(Text, nullable=True)
    move_played: Mapped[str] = mapped_column(String(50), nullable=False)
    best_move: Mapped[str] = mapped_column(String(50), nullable=False)
    evaluation_before: Mapped[float] = mapped_column(Float, nullable=False)
    evaluation_after: Mapped[float] = mapped_column(Float, nullable=False)
    move_number: Mapped[int] = mapped_column(Integer, nullable=False)
    counter: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # Spaced repetition fields
    easiness_factor: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    interval: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    user = relationship("User", back_populates="bad_moves")
    game = relationship("Game", back_populates="bad_moves")
