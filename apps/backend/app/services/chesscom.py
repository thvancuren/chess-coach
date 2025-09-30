"""Chess.com API integration service."""

import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.models import Game, GameResult, Side
from app.db import SessionLocal


class ChessComService:
    """Service for fetching and processing Chess.com data."""
    
    BASE_URL = "https://api.chess.com/pub"
    USER_AGENT = os.getenv("CHESSCOM_USER_AGENT", "chess-coach/0.1")
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get_user_games(self, username: str, from_date: Optional[str] = None, 
                      to_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch all games for a user within date range."""
        games = []
        
        # Parse date range
        start_date = self._parse_date(from_date) if from_date else datetime(2020, 1, 1)
        end_date = self._parse_date(to_date) if to_date else datetime.now()
        
        # Generate monthly date range
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            year_month = current_date.strftime("%Y/%m")
            monthly_games = self._get_monthly_games(username, year_month)
            games.extend(monthly_games)
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return games
    
    def _get_monthly_games(self, username: str, year_month: str) -> List[Dict[str, Any]]:
        """Fetch games for a specific month."""
        url = f"{self.BASE_URL}/player/{username}/games/{year_month}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            games = data.get("games", [])
            processed_games = []
            
            for game_data in games:
                processed_game = self._process_game_data(game_data, username)
                if processed_game:
                    processed_games.append(processed_game)
            
            return processed_games
            
        except requests.RequestException as e:
            print(f"Error fetching games for {username} {year_month}: {e}")
            return []
    
    def _process_game_data(self, game_data: Dict[str, Any], username: str) -> Optional[Dict[str, Any]]:
        """Process raw game data into our format."""
        try:
            # Extract basic info
            pgn = game_data.get("pgn", "")
            if not pgn:
                return None
            
            # Determine user's side
            white_player = game_data.get("white", {}).get("username", "")
            black_player = game_data.get("black", {}).get("username", "")
            
            if username.lower() not in [white_player.lower(), black_player.lower()]:
                return None
            
            user_side = Side.WHITE if username.lower() == white_player.lower() else Side.BLACK
            
            # Parse PGN headers
            headers = self._parse_pgn_headers(pgn)
            
            # Extract ECO and opening
            eco = headers.get("ECO", "")
            opening = headers.get("Opening", "")
            
            # Parse result
            result_str = headers.get("Result", "")
            result = self._parse_result(result_str)
            
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
            
            return {
                "pgn": pgn,
                "json": game_data,
                "eco": eco,
                "opening": opening,
                "result": result,
                "time_control": time_control,
                "white": white_player,
                "black": black_player,
                "started_at": started_at,
                "user_side": user_side,
            }
            
        except Exception as e:
            print(f"Error processing game data: {e}")
            return None
    
    def _parse_pgn_headers(self, pgn: str) -> Dict[str, str]:
        """Parse PGN headers into a dictionary."""
        headers = {}
        lines = pgn.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                # Extract key-value pairs
                match = re.match(r'\[(\w+)\s+"([^"]*)"\]', line)
                if match:
                    key, value = match.groups()
                    headers[key] = value
        
        return headers
    
    def _parse_result(self, result_str: str) -> Optional[GameResult]:
        """Parse PGN result string into GameResult enum."""
        if result_str == "1-0":
            return GameResult.WHITE_WINS
        elif result_str == "0-1":
            return GameResult.BLACK_WINS
        elif result_str == "1/2-1/2":
            return GameResult.DRAW
        return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse YYYY-MM date string into datetime."""
        return datetime.strptime(date_str, "%Y-%m")
    
    def save_games(self, username: str, games: List[Dict[str, Any]]) -> int:
        """Save games to database, avoiding duplicates."""
        db = SessionLocal()
        saved_count = 0
        
        try:
            for game_data in games:
                # Check if game already exists (by PGN hash or other unique identifier)
                existing_game = db.query(Game).filter(
                    Game.username == username,
                    Game.pgn == game_data["pgn"]
                ).first()
                
                if existing_game:
                    continue
                
                # Create new game
                game = Game(
                    username=username,
                    site="chesscom",
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
            return 0
        finally:
            db.close()

