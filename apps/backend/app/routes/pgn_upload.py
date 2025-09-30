"""PGN file upload API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.pgn import PGNService

router = APIRouter()


@router.post("/upload")
async def upload_pgn_file(
    username: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and parse a PGN file."""
    try:
        # Validate file type
        if not file.filename.endswith('.pgn'):
            raise HTTPException(status_code=400, detail="File must be a .pgn file")
        
        # Read file content
        content = await file.read()
        pgn_content = content.decode('utf-8')
        
        # Parse PGN content
        pgn_service = PGNService()
        games_data = pgn_service.parse_pgn_file(pgn_content, username)
        
        if not games_data:
            raise HTTPException(status_code=400, detail="No valid games found in PGN file")
        
        # Save games to database
        saved_count = pgn_service.save_games(username, games_data)
        
        return {
            "message": f"Successfully uploaded {saved_count} games from PGN file",
            "username": username,
            "total_games": len(games_data),
            "saved_games": saved_count,
            "skipped_games": len(games_data) - saved_count
        }
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file encoding. Please ensure the file is UTF-8 encoded.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-text")
async def upload_pgn_text(
    username: str = Form(...),
    pgn_text: str = Form(...),
    db: Session = Depends(get_db)
):
    """Upload PGN content as text."""
    try:
        if not pgn_text.strip():
            raise HTTPException(status_code=400, detail="PGN content cannot be empty")
        
        # Parse PGN content
        pgn_service = PGNService()
        games_data = pgn_service.parse_pgn_file(pgn_text, username)
        
        if not games_data:
            raise HTTPException(status_code=400, detail="No valid games found in PGN text")
        
        # Save games to database
        saved_count = pgn_service.save_games(username, games_data)
        
        return {
            "message": f"Successfully uploaded {saved_count} games from PGN text",
            "username": username,
            "total_games": len(games_data),
            "saved_games": saved_count,
            "skipped_games": len(games_data) - saved_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

