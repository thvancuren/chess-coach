"""Background task workers using RQ."""

import os
import redis
from rq import Queue, Worker
from typing import Optional, Dict, Any

from app.services.chesscom import ChessComService
from app.services.stockfish import StockfishService
from app.services.puzzles import PuzzleService
from app.db import SessionLocal
from app.models import AnalysisJob, Game, Move
from app.schemas import AnalysisProgressMessage

# Redis connection
redis_conn = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))


def publish_progress_update(username: str, message: AnalysisProgressMessage) -> None:
    """Publish job progress updates via Redis pub/sub."""
    channel = f"analysis_progress:{username}"
    redis_conn.publish(channel, message.json())


# Task queues
import_queue = Queue("import", connection=redis_conn)
analysis_queue = Queue("analysis", connection=redis_conn)
puzzle_queue = Queue("puzzles", connection=redis_conn)


def enqueue_import_job(username: str, from_date: Optional[str] = None, 
                      to_date: Optional[str] = None) -> str:
    """Enqueue a Chess.com import job."""
    job = import_queue.enqueue(
        import_chesscom_games,
        username, from_date, to_date,
        job_timeout="1h"
    )
    return job.id


def enqueue_analysis_job(username: str, max_depth: int = 20) -> str:
    """Enqueue a game analysis job."""
    job = analysis_queue.enqueue(
        analyze_games,
        username, max_depth,
        job_timeout="2h"
    )
    return job.id


def enqueue_puzzle_job(username: str) -> str:
    """Enqueue a puzzle generation job."""
    job = puzzle_queue.enqueue(
        generate_puzzles,
        username,
        job_timeout="30m"
    )
    return job.id


def import_chesscom_games(username: str, from_date: Optional[str] = None, 
                         to_date: Optional[str] = None) -> Dict[str, Any]:
    """Import games from Chess.com."""
    db = SessionLocal()
    
    try:
        # Create job record
        job = AnalysisJob(
            username=username,
            job_type="import",
            status="running"
        )
        db.add(job)
        db.commit()
        
        # Send progress update
        publish_progress_update(username, AnalysisProgressMessage(
            username=username,
            job_type="import",
            status="running",
            progress=0,
            total_items=None,
            processed_items=0,
            message="Starting import..."
        ))
        
        # Import games
        chesscom_service = ChessComService()
        games = chesscom_service.get_user_games(username, from_date, to_date)
        
        job.total_items = len(games)
        job.processed_items = 0
        db.commit()
        
        # Save games in batches
        batch_size = 10
        saved_count = 0
        
        for i in range(0, len(games), batch_size):
            batch = games[i:i + batch_size]
            saved_count += chesscom_service.save_games(username, batch)
            
            job.processed_items = i + len(batch)
            job.progress = int((job.processed_items / job.total_items) * 100)
            db.commit()
            
            # Send progress update
            publish_progress_update(username, AnalysisProgressMessage(
                username=username,
                job_type="import",
                status="running",
                progress=job.progress,
                total_items=job.total_items,
                processed_items=job.processed_items,
                message=f"Imported {saved_count} games..."
            ))
        
        # Mark job as completed
        job.status = "completed"
        job.progress = 100
        db.commit()
        
        # Send final update
        publish_progress_update(username, AnalysisProgressMessage(
            username=username,
            job_type="import",
            status="completed",
            progress=100,
            total_items=job.total_items,
            processed_items=job.processed_items,
            message=f"Import completed! {saved_count} games imported."
        ))
        
        return {"imported": saved_count, "total": len(games)}
        
    except Exception as e:
        # Mark job as failed
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
        
        # Send error update
        publish_progress_update(username, AnalysisProgressMessage(
            username=username,
            job_type="import",
            status="failed",
            progress=0,
            total_items=None,
            processed_items=0,
            message=f"Import failed: {str(e)}"
        ))
        
        raise e
    finally:
        db.close()


def analyze_games(username: str, max_depth: int = 20) -> Dict[str, Any]:
    """Analyze games with Stockfish."""
    db = SessionLocal()
    
    try:
        # Create job record
        job = AnalysisJob(
            username=username,
            job_type="analyze",
            status="running"
        )
        db.add(job)
        db.commit()
        
        # Get games to analyze - find games that don't have any moves
        from sqlalchemy import func
        
        # Get all games for user
        all_games = db.query(Game).filter(Game.username == username).all()
        print(f"Total games for {username}: {len(all_games)}")
        
        # Filter games that don't have moves
        games_without_moves = []
        for i, game in enumerate(all_games):
            move_count = db.query(Move).filter(Move.game_id == game.id).count()
            if i < 3:  # Debug first 3 games
                print(f"Game {game.id}: {move_count} moves")
            if move_count == 0:
                games_without_moves.append(game)
        
        print(f"Games without moves for {username}: {len(games_without_moves)}")
        games = games_without_moves
        job.total_items = len(games)
        job.processed_items = 0
        db.commit()
        
        # Send progress update
        publish_progress_update(username, AnalysisProgressMessage(
            username=username,
            job_type="analyze",
            status="running",
            progress=0,
            total_items=job.total_items,
            processed_items=0,
            message="Starting analysis..."
        ))
        
        # Analyze games with Stockfish
        with StockfishService(depth=max_depth) as stockfish:
            analyzed_count = 0
            
            for i, game in enumerate(games):
                try:
                    # Analyze the game
                    moves_data = stockfish.analyze_game(game.pgn, username)
                    
                    # Save moves
                    if moves_data:
                        stockfish.save_moves(str(game.id), moves_data)
                        analyzed_count += 1
                    
                    # Update progress
                    job.processed_items = i + 1
                    job.progress = int((job.processed_items / job.total_items) * 100)
                    db.commit()
                    
                    # Send progress update
                    publish_progress_update(username, AnalysisProgressMessage(
                        username=username,
                        job_type="analyze",
                        status="running",
                        progress=job.progress,
                        total_items=job.total_items,
                        processed_items=job.processed_items,
                        message=f"Analyzed {analyzed_count} games..."
                    ))
                    
                except Exception as e:
                    print(f"Error analyzing game {game.id}: {e}")
                    continue
        
        # Mark job as completed
        job.status = "completed"
        job.progress = 100
        db.commit()
        
        # Send final update
        publish_progress_update(username, AnalysisProgressMessage(
            username=username,
            job_type="analyze",
            status="completed",
            progress=100,
            total_items=job.total_items,
            processed_items=job.processed_items,
            message=f"Analysis completed! {analyzed_count} games analyzed."
        ))
        
        return {"analyzed": analyzed_count, "total": len(games)}
        
    except Exception as e:
        # Mark job as failed
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
        
        # Send error update
        publish_progress_update(username, AnalysisProgressMessage(
            username=username,
            job_type="analyze",
            status="failed",
            progress=0,
            total_items=None,
            processed_items=0,
            message=f"Analysis failed: {str(e)}"
        ))
        
        raise e
    finally:
        db.close()


def generate_puzzles(username: str) -> Dict[str, Any]:
    """Generate puzzles from user's blunders."""
    db = SessionLocal()
    
    try:
        # Create job record
        job = AnalysisJob(
            username=username,
            job_type="puzzle",
            status="running"
        )
        db.add(job)
        db.commit()
        
        # Send progress update
        publish_progress_update(username, AnalysisProgressMessage(
            username=username,
            job_type="puzzle",
            status="running",
            progress=0,
            total_items=None,
            processed_items=0,
            message="Starting puzzle generation..."
        ))
        
        # Generate puzzles
        puzzle_service = PuzzleService()
        generated_count = puzzle_service.generate_puzzles_from_blunders(username)
        
        # Mark job as completed
        job.status = "completed"
        job.progress = 100
        job.processed_items = generated_count
        db.commit()
        
        # Send final update
        publish_progress_update(username, AnalysisProgressMessage(
            username=username,
            job_type="puzzle",
            status="completed",
            progress=100,
            total_items=None,
            processed_items=generated_count,
            message=f"Puzzle generation completed! {generated_count} puzzles created."
        ))
        
        return {"generated": generated_count}
        
    except Exception as e:
        # Mark job as failed
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
        
        # Send error update
        publish_progress_update(username, AnalysisProgressMessage(
            username=username,
            job_type="puzzle",
            status="failed",
            progress=0,
            total_items=None,
            processed_items=0,
            message=f"Puzzle generation failed: {str(e)}"
        ))
        
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    # Start worker
    worker = Worker([import_queue, analysis_queue, puzzle_queue], connection=redis_conn)
    worker.work()
