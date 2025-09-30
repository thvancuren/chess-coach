"""Puzzles API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import PuzzleResponse
from app.models import Puzzle
from app.worker import enqueue_puzzle_job

router = APIRouter()


@router.get("/", response_model=List[PuzzleResponse])
async def get_puzzles(
    username: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get puzzles for a user."""
    puzzles = db.query(Puzzle).join(Puzzle.game).filter(
        Puzzle.game.has(username=username)
    ).order_by(Puzzle.created_at.desc()).limit(limit).all()
    
    return puzzles


@router.post("/generate")
async def generate_puzzles(
    username: str,
    db: Session = Depends(get_db)
):
    """Generate puzzles from user's blunders."""
    try:
        # Enqueue puzzle generation job
        job_id = enqueue_puzzle_job(username=username)
        
        return {
            "message": "Puzzle generation job queued",
            "job_id": job_id,
            "username": username
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Puzzle generation failed: {str(e)}")


@router.get("/{puzzle_id}", response_model=PuzzleResponse)
async def get_puzzle(
    puzzle_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific puzzle."""
    puzzle = db.query(Puzzle).filter(Puzzle.id == puzzle_id).first()
    
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    
    return puzzle

