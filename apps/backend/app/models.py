"""SQLAlchemy models for the chess coach application."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime, 
    ForeignKey, JSON, Boolean, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, CHAR


class GUID(TypeDecorator):
    """Platform-independent GUID/UUID type."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PGUUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        import uuid

        if value is None:
            return value

        if isinstance(value, uuid.UUID):
            return value if dialect.name == 'postgresql' else str(value)

        return value if dialect.name == 'postgresql' else str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        import uuid

        if value is None:
            return value

        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


Base = declarative_base()


class MistakeType(str, Enum):
    """Mistake classification based on evaluation swing."""
    NONE = "none"
    INACCURACY = "inacc"  # >= 90cp
    MISTAKE = "mistake"   # >= 150cp
    BLUNDER = "blunder"   # >= 200cp


class GameResult(str, Enum):
    """Chess game result."""
    WHITE_WINS = "1-0"
    BLACK_WINS = "0-1"
    DRAW = "1/2-1/2"


class Side(str, Enum):
    """Chess side."""
    WHITE = "white"
    BLACK = "black"


class Game(Base):
    """Chess game model."""
    __tablename__ = "games"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), nullable=False, index=True)
    site = Column(String(20), nullable=False, default="chesscom")
    pgn = Column(Text, nullable=False)
    json = Column(JSON, nullable=True)
    eco = Column(String(10), nullable=True, index=True)
    opening = Column(String(200), nullable=True)
    result = Column(SQLEnum(GameResult), nullable=True)
    time_control = Column(String(50), nullable=True)
    white = Column(String(100), nullable=True)
    black = Column(String(100), nullable=True)
    started_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    moves = relationship("Move", back_populates="game", cascade="all, delete-orphan")
    features = relationship("GameFeatures", back_populates="game", uselist=False)
    puzzles = relationship("Puzzle", back_populates="game")


class Move(Base):
    """Individual chess move model."""
    __tablename__ = "moves"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    game_id = Column(GUID(), ForeignKey("games.id"), nullable=False, index=True)
    ply = Column(Integer, nullable=False)
    fen = Column(String(100), nullable=False)
    san = Column(String(20), nullable=False)
    side = Column(SQLEnum(Side), nullable=False)
    time_left_ms = Column(Integer, nullable=True)
    
    # Stockfish analysis
    sf_eval_cp = Column(Integer, nullable=True)  # Centipawns
    sf_mate = Column(Integer, nullable=True)     # Mate in N moves
    sf_bestmove_uci = Column(String(10), nullable=True)
    sf_pv = Column(Text, nullable=True)          # Principal variation
    mistake_tag = Column(SQLEnum(MistakeType), default=MistakeType.NONE)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    game = relationship("Game", back_populates="moves")
    neighbors = relationship("HumanNeighbor", back_populates="move")


class GameFeatures(Base):
    """Aggregated game features and statistics."""
    __tablename__ = "features"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    game_id = Column(GUID(), ForeignKey("games.id"), nullable=False, unique=True)
    counts_by_motif = Column(JSON, nullable=True)
    blunder_rate_by_phase = Column(JSON, nullable=True)
    time_profile = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    game = relationship("Game", back_populates="features")


class HumanNeighbor(Base):
    """Human reference for a specific move position."""
    __tablename__ = "neighbors"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    move_id = Column(GUID(), ForeignKey("moves.id"), nullable=False, index=True)
    ref_game_id = Column(String(50), nullable=False)  # Reference to GM game
    ref_ply = Column(Integer, nullable=False)
    similarity = Column(Float, nullable=False)
    human_choice_san = Column(String(20), nullable=False)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    move = relationship("Move", back_populates="neighbors")


class Puzzle(Base):
    """Generated puzzle from user's blunders."""
    __tablename__ = "puzzles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    source_move_id = Column(GUID(), ForeignKey("moves.id"), nullable=False)
    game_id = Column(GUID(), ForeignKey("games.id"), nullable=False)
    fen_start = Column(String(100), nullable=False)
    solution_san = Column(JSON, nullable=False)  # Array of SAN moves
    motif = Column(String(50), nullable=True)
    strength = Column(Integer, nullable=False, default=1)  # 1-5 difficulty
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    game = relationship("Game", back_populates="puzzles")


class AnalysisJob(Base):
    """Background analysis job tracking."""
    __tablename__ = "analysis_jobs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), nullable=False, index=True)
    job_type = Column(String(50), nullable=False)  # import, analyze, puzzle
    status = Column(String(20), nullable=False, default="pending")  # pending, running, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    total_items = Column(Integer, nullable=True)
    processed_items = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


