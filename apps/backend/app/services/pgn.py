"""PGN file parsing and processing service."""

import chess
import chess.pgn
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models import Game, GameResult, Side
from app.db import SessionLocal


class PGNService:
    """Service for parsing and processing PGN files."""
    
    def __init__(self):
        pass
    
    def parse_pgn_file(self, pgn_content: str, username: str) -> List[Dict[str, Any]]:
        """Parse PGN file content and extract games."""
        games_data = []
        
        try:
            # Parse PGN content
            pgn_io = io.StringIO(pgn_content)
            
            while True:
                game = chess.pgn.read_game(pgn_io)
                if not game:
                    break
                
                # Process the game
                game_data = self._process_game(game, username)
                if game_data:
                    games_data.append(game_data)
            
            return games_data
            
        except Exception as e:
            print(f"Error parsing PGN: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _process_game(self, game: chess.pgn.Game, username: str) -> Optional[Dict[str, Any]]:
        """Process a single game from PGN."""
        try:
            # Extract headers
            headers = game.headers
            
            # Determine user's side (try to match username with players)
            white_player = headers.get("White", "")
            black_player = headers.get("Black", "")
            
            # Check if username matches either player
            user_side = None
            if username.lower() in white_player.lower():
                user_side = Side.WHITE
            elif username.lower() in black_player.lower():
                user_side = Side.BLACK
            else:
                # If username doesn't match, assume they played as white
                user_side = Side.WHITE
            
            # Extract ECO and opening
            eco = headers.get("ECO", "")
            opening = headers.get("Opening", "")
            
            # Parse result
            result_str = headers.get("Result", "")
            result_enum = self._parse_result(result_str)
            
            # Extract time control
            time_control = headers.get("TimeControl", "")
            
            # Parse start time
            started_at = None
            if "UTCDate" in headers and "UTCTime" in headers:
                try:
                    date_str = f"{headers['UTCDate']} {headers['UTCTime']}"
                    started_at = datetime.strptime(date_str, "%Y.%m.%d %H:%M:%S")
                except ValueError:
                    pass
            elif "Date" in headers:
                try:
                    # Try different date formats
                    date_str = headers["Date"]
                    if "." in date_str:
                        started_at = datetime.strptime(date_str, "%Y.%m.%d")
                    else:
                        started_at = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    pass
            
            # Convert game to PGN string
            pgn_string = str(game)
            
            return {
                "pgn": pgn_string,
                "json": {
                    "headers": dict(headers),
                    "user_side": user_side.value,
                    "result": result_enum.value if result_enum else None,
                },
                "eco": eco,
                "opening": opening,
                "result": result_enum,
                "time_control": time_control,
                "white": white_player,
                "black": black_player,
                "started_at": started_at,
            }
            
        except Exception as e:
            print(f"Error processing game: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_result(self, result_str: str) -> Optional[GameResult]:
        """Parse game result string."""
        result_str = result_str.strip()
        
        if result_str == "1-0":
            return GameResult.WHITE_WINS
        elif result_str == "0-1":
            return GameResult.BLACK_WINS
        elif result_str == "1/2-1/2":
            return GameResult.DRAW
        else:
            return None
    
    def save_games(self, username: str, games: List[Dict[str, Any]]) -> int:
        """Save games to database, avoiding duplicates."""
        db = SessionLocal()
        saved_count = 0
        
        try:
            for game_data in games:
                # Check if game already exists (by PGN content)
                existing_game = db.query(Game).filter(
                    Game.username == username,
                    Game.pgn == game_data["pgn"]
                ).first()
                
                if existing_game:
                    continue
                
                # Create new game
                game = Game(
                    username=username,
                    site="pgn",  # Mark as PGN upload
                    pgn=game_data["pgn"],
                    json=game_data["json"],
                    eco=game_data["eco"],
                    opening=game_data["opening"],
                    result=game_data["result"],
                    time_control=game_data["time_control"],
                    white=game_data["white"],
                    black=game_data["black"],
                    started_at=game_data["started_at"],
                )
                
                db.add(game)
                saved_count += 1
            
            db.commit()
            return saved_count
            
        except Exception as e:
            db.rollback()
            print(f"Error saving games: {e}")
            import traceback
            traceback.print_exc()
            return 0
        finally:
            db.close()
