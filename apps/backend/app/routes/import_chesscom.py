"""Chess.com import API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import ChessComImportRequest
from app.services.chesscom import ChessComService
from app.worker import enqueue_import_job

router = APIRouter()


@router.post("/chesscom")
async def import_chesscom_games(
    request: ChessComImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Import games from Chess.com for a user."""
    try:
        # Enqueue import job
        job_id = enqueue_import_job(
            username=request.username,
            from_date=request.from_date,
            to_date=request.to_date
        )
        
        return {
            "message": "Import job queued",
            "job_id": job_id,
            "username": request.username
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/status/{username}")
async def get_import_status(username: str, db: Session = Depends(get_db)):
    """Get import status for a user."""
    from app.models import AnalysisJob
    
    # Get latest import job for user
    job = db.query(AnalysisJob).filter(
        AnalysisJob.username == username,
        AnalysisJob.job_type == "import"
    ).order_by(AnalysisJob.created_at.desc()).first()
    
    if not job:
        return {
            "username": username,
            "status": "not_found",
            "message": "No import job found"
        }
    
    return {
        "username": username,
        "job_id": str(job.id),
        "status": job.status,
        "progress": job.progress,
        "total_items": job.total_items,
        "processed_items": job.processed_items,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }

