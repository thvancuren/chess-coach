"""Human references API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import HumanNeighborResponse
from app.models import Move
from app.services.human_index import HumanIndexService

router = APIRouter()


@router.get("/neighbors", response_model=List[HumanNeighborResponse])
async def get_human_neighbors(
    move_id: str,
    k: int = 5,
    db: Session = Depends(get_db)
):
    """Get human references for a specific move."""
    # Get the move
    move = db.query(Move).filter(Move.id == move_id).first()
    
    if not move:
        raise HTTPException(status_code=404, detail="Move not found")
    
    # Find human neighbors
    human_service = HumanIndexService()
    neighbors = human_service.find_neighbors(move, k)
    
    # Save neighbors to database
    if neighbors:
        human_service.save_neighbors(move_id, neighbors)
    
    return neighbors

