"""Game analysis API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import BatchAnalysisRequest, AnalysisStatusResponse
from app.worker import enqueue_analysis_job

router = APIRouter()


@router.post("/batch")
async def analyze_games(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze games with Stockfish."""
    try:
        # Enqueue analysis job
        job_id = enqueue_analysis_job(
            username=request.username,
            max_depth=request.max_depth
        )
        
        return {
            "message": "Analysis job queued",
            "job_id": job_id,
            "username": request.username
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/status")
async def get_analysis_status(
    username: str,
    db: Session = Depends(get_db)
) -> AnalysisStatusResponse:
    """Get analysis status for a user."""
    from app.models import AnalysisJob
    
    # Get latest analysis job for user
    job = db.query(AnalysisJob).filter(
        AnalysisJob.username == username,
        AnalysisJob.job_type == "analyze"
    ).order_by(AnalysisJob.created_at.desc()).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="No analysis job found")
    
    return AnalysisStatusResponse(
        username=job.username,
        job_type=job.job_type,
        status=job.status,
        progress=job.progress,
        total_items=job.total_items,
        processed_items=job.processed_items,
        error_message=job.error_message,
        created_at=job.created_at,
        completed_at=job.completed_at
    )

