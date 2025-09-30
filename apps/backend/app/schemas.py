"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


# Request schemas
class ChessComImportRequest(BaseModel):
    """Request to import games from Chess.com."""
    username: str = Field(..., min_length=1, max_length=100)
    from_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$")
    to_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$")


class BatchAnalysisRequest(BaseModel):
    """Request to analyze games with Stockfish."""
    username: str = Field(..., min_length=1, max_length=100)
    max_depth: Optional[int] = Field(20, ge=1, le=30)


class SparringSessionRequest(BaseModel):
    """Request to create a sparring session."""
    username: str = Field(..., min_length=1, max_length=100)
    difficulty: int = Field(..., ge=1, le=5)
    style_hints: Optional[Dict[str, Any]] = None


# Response schemas
class MoveResponse(BaseModel):
    """Individual move with analysis."""
    id: UUID
    ply: int
    fen: str
    san: str
    side: str
    time_left_ms: Optional[int]
    sf_eval_cp: Optional[int]
    sf_mate: Optional[int]
    sf_bestmove_uci: Optional[str]
    sf_pv: Optional[str]
    mistake_tag: str

    class Config:
        from_attributes = True


class GameResponse(BaseModel):
    """Game with basic metadata."""
    id: UUID
    username: str
    site: str
    eco: Optional[str]
    opening: Optional[str]
    result: Optional[str]
    time_control: Optional[str]
    white: Optional[str]
    black: Optional[str]
    started_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class GameDetailResponse(GameResponse):
    """Detailed game with moves and analysis."""
    pgn: str
    moves: List[MoveResponse]
    features: Optional[Dict[str, Any]]


class PuzzleResponse(BaseModel):
    """Generated puzzle."""
    id: UUID
    fen_start: str
    solution_san: List[str]
    motif: Optional[str]
    strength: int
    created_at: datetime

    class Config:
        from_attributes = True


class HumanNeighborResponse(BaseModel):
    """Human reference for a position."""
    ref_game_id: str
    ref_ply: int
    similarity: float
    human_choice_san: str
    meta: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class AnalysisStatusResponse(BaseModel):
    """Analysis job status."""
    username: str
    job_type: str
    status: str
    progress: int
    total_items: Optional[int]
    processed_items: int
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


class StatsSummaryResponse(BaseModel):
    """User statistics summary."""
    username: str
    total_games: int
    blunder_rate: float
    mistake_rate: float
    inaccuracy_rate: float
    blunder_rate_by_phase: Dict[str, float]
    common_motifs: List[Dict[str, Any]]
    time_profile: Optional[Dict[str, Any]]


class SparringSessionResponse(BaseModel):
    """Sparring session info."""
    session_id: UUID
    username: str
    difficulty: int
    style_hints: Optional[Dict[str, Any]]
    created_at: datetime


# WebSocket message schemas
class AnalysisProgressMessage(BaseModel):
    """WebSocket message for analysis progress."""
    username: str
    job_type: str
    status: str
    progress: int
    total_items: Optional[int]
    processed_items: int
    message: Optional[str]

