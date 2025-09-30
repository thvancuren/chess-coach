"""Games API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import GameResponse, GameDetailResponse, StatsSummaryResponse
from app.models import Game, Move, MistakeType

router = APIRouter()


@router.get("/", response_model=List[GameResponse])
async def get_games(
    username: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get games for a user."""
    games = db.query(Game).filter(
        Game.username == username
    ).order_by(Game.started_at.desc()).offset(offset).limit(limit).all()
    
    return games


@router.get("/{game_id}", response_model=GameDetailResponse)
async def get_game_detail(
    game_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed game information with moves and analysis."""
    import uuid
    
    try:
        game_uuid = uuid.UUID(game_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid game ID format")
    
    game = db.query(Game).filter(Game.id == game_uuid).first()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get moves with analysis
    moves = db.query(Move).filter(
        Move.game_id == game_uuid
    ).order_by(Move.ply).all()
    
    # Get game features
    features = None
    if game.features:
        features = {
            "counts_by_motif": game.features.counts_by_motif,
            "blunder_rate_by_phase": game.features.blunder_rate_by_phase,
            "time_profile": game.features.time_profile,
        }
    
    return GameDetailResponse(
        id=game.id,
        username=game.username,
        site=game.site,
        eco=game.eco,
        opening=game.opening,
        result=game.result.value if game.result else None,
        time_control=game.time_control,
        white=game.white,
        black=game.black,
        started_at=game.started_at,
        created_at=game.created_at,
        pgn=game.pgn,
        moves=[
            {
                "id": move.id,
                "ply": move.ply,
                "fen": move.fen,
                "san": move.san,
                "side": move.side.value,
                "time_left_ms": move.time_left_ms,
                "sf_eval_cp": move.sf_eval_cp,
                "sf_mate": move.sf_mate,
                "sf_bestmove_uci": move.sf_bestmove_uci,
                "sf_pv": move.sf_pv,
                "mistake_tag": move.mistake_tag.value,
            }
            for move in moves
        ],
        features=features
    )


@router.get("/stats/summary", response_model=StatsSummaryResponse)
async def get_stats_summary(
    username: str,
    db: Session = Depends(get_db)
):
    """Get user statistics summary."""
    # Get total games
    total_games = db.query(Game).filter(Game.username == username).count()
    
    if total_games == 0:
        return StatsSummaryResponse(
            username=username,
            total_games=0,
            blunder_rate=0.0,
            mistake_rate=0.0,
            inaccuracy_rate=0.0,
            blunder_rate_by_phase={},
            common_motifs=[],
            time_profile=None
        )
    
    # Get moves with mistakes
    moves = db.query(Move).join(Move.game).filter(
        Move.game.has(username=username)
    ).all()
    
    total_moves = len(moves)
    blunders = len([m for m in moves if m.mistake_tag == MistakeType.BLUNDER])
    mistakes = len([m for m in moves if m.mistake_tag == MistakeType.MISTAKE])
    inaccuracies = len([m for m in moves if m.mistake_tag == MistakeType.INACCURACY])
    
    # Calculate rates
    blunder_rate = (blunders / total_moves) * 100 if total_moves > 0 else 0.0
    mistake_rate = (mistakes / total_moves) * 100 if total_moves > 0 else 0.0
    inaccuracy_rate = (inaccuracies / total_moves) * 100 if total_moves > 0 else 0.0
    
    # Calculate blunder rate by phase (simplified)
    blunder_rate_by_phase = {
        "opening": 0.0,
        "middlegame": 0.0,
        "endgame": 0.0
    }
    
    # Get common motifs (simplified)
    common_motifs = [
        {"motif": "tactics", "count": blunders + mistakes},
        {"motif": "positional", "count": inaccuracies},
    ]
    
    return StatsSummaryResponse(
        username=username,
        total_games=total_games,
        blunder_rate=blunder_rate,
        mistake_rate=mistake_rate,
        inaccuracy_rate=inaccuracy_rate,
        blunder_rate_by_phase=blunder_rate_by_phase,
        common_motifs=common_motifs,
        time_profile=None
    )

