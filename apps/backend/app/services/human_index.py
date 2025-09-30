"""Human database indexing and nearest neighbor lookup service."""

import os
import sqlite3
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.neighbors import NearestNeighbors
import chess

from app.models import HumanNeighbor, Move
from app.db import SessionLocal


class HumanIndexService:
    """Service for indexing GM games and finding human references."""
    
    def __init__(self, index_path: Optional[str] = None):
        self.index_path = index_path or os.getenv("HUMAN_INDEX_PATH", "/data/human_index.sqlite")
        self.nn_model = None
        self.feature_vectors = []
        self.game_references = []
    
    def build_index(self, lichess_file_path: str, sample_size: int = 10000) -> bool:
        """Build human game index from Lichess database file."""
        try:
            # This is a stub implementation
            # In practice, you would:
            # 1. Parse the Lichess PGN file
            # 2. Extract GM games
            # 3. Compute feature vectors for each position
            # 4. Build nearest neighbor index
            
            print(f"Building human index from {lichess_file_path} (sample size: {sample_size})")
            
            # Create SQLite database for human references
            conn = sqlite3.connect(self.index_path)
            cursor = conn.cursor()
            
            # Create table for human positions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS human_positions (
                    id INTEGER PRIMARY KEY,
                    fen TEXT,
                    eco TEXT,
                    side INTEGER,
                    pawn_hash TEXT,
                    eval_band INTEGER,
                    piece_activity REAL,
                    human_choice_san TEXT,
                    game_id TEXT,
                    ply INTEGER,
                    meta TEXT
                )
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_human_positions_features 
                ON human_positions(eco, side, pawn_hash, eval_band)
            """)
            
            conn.commit()
            conn.close()
            
            print("Human index built successfully")
            return True
            
        except Exception as e:
            print(f"Error building human index: {e}")
            return False
    
    def find_neighbors(self, move: Move, k: int = 5) -> List[Dict[str, Any]]:
        """Find k nearest human neighbors for a given move."""
        try:
            # Extract features from the move
            features = self._extract_features(move)
            
            # Query SQLite database for similar positions
            conn = sqlite3.connect(self.index_path)
            cursor = conn.cursor()
            
            # Simple similarity search based on ECO, side, and pawn structure
            query = """
                SELECT * FROM human_positions 
                WHERE eco = ? AND side = ? AND pawn_hash = ?
                ORDER BY ABS(eval_band - ?) + ABS(piece_activity - ?)
                LIMIT ?
            """
            
            cursor.execute(query, (
                features["eco"],
                features["side"],
                features["pawn_hash"],
                features["eval_band"],
                features["piece_activity"],
                k
            ))
            
            results = cursor.fetchall()
            conn.close()
            
            # Convert to response format
            neighbors = []
            for row in results:
                neighbor = {
                    "ref_game_id": row[8],  # game_id
                    "ref_ply": row[9],      # ply
                    "similarity": 1.0 - abs(row[6] - features["piece_activity"]) / 10.0,  # Simple similarity
                    "human_choice_san": row[7],  # human_choice_san
                    "meta": json.loads(row[10]) if row[10] else {}  # meta
                }
                neighbors.append(neighbor)
            
            return neighbors
            
        except Exception as e:
            print(f"Error finding neighbors: {e}")
            return []
    
    def _extract_features(self, move: Move) -> Dict[str, Any]:
        """Extract feature vector from a move position."""
        import chess
        
        board = chess.Board(move.fen)
        
        # ECO code (simplified - in practice, use a proper opening database)
        eco = self._get_eco_code(board)
        
        # Side (0 for white, 1 for black)
        side = 0 if move.side.value == "white" else 1
        
        # Pawn structure hash
        pawn_hash = self._get_pawn_hash(board)
        
        # Evaluation band (-1, 0, 1)
        eval_band = self._get_eval_band(move.sf_eval_cp)
        
        # Piece activity (simplified)
        piece_activity = self._get_piece_activity(board)
        
        return {
            "eco": eco,
            "side": side,
            "pawn_hash": pawn_hash,
            "eval_band": eval_band,
            "piece_activity": piece_activity,
        }
    
    def _get_eco_code(self, board: chess.Board) -> str:
        """Get ECO code for position (simplified)."""
        # This is a very simplified implementation
        # In practice, you'd use a proper opening database
        
        # Count pieces to determine opening phase
        piece_count = len(board.piece_map())
        
        if piece_count >= 30:
            return "A00"  # Opening
        elif piece_count >= 20:
            return "B00"  # Middlegame
        else:
            return "C00"  # Endgame
    
    def _get_pawn_hash(self, board: chess.Board) -> str:
        """Get hash of pawn structure."""
        pawns = []
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN:
                pawns.append(f"{piece.color}{square}")
        
        pawns.sort()
        return hashlib.md5("".join(pawns).encode()).hexdigest()[:8]
    
    def _get_eval_band(self, eval_cp: Optional[int]) -> int:
        """Convert evaluation to band (-1, 0, 1)."""
        if eval_cp is None:
            return 0
        elif eval_cp > 100:
            return 1
        elif eval_cp < -100:
            return -1
        else:
            return 0
    
    def _get_piece_activity(self, board: chess.Board) -> float:
        """Calculate piece activity score."""
        activity = 0.0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Count legal moves for this piece
                legal_moves = [move for move in board.legal_moves if move.from_square == square]
                activity += len(legal_moves) * (1.0 if piece.piece_type != chess.PAWN else 0.5)
        
        return activity
    
    def save_neighbors(self, move_id: str, neighbors: List[Dict[str, Any]]) -> int:
        """Save human neighbors to database."""
        db = SessionLocal()
        saved_count = 0
        
        try:
            for neighbor_data in neighbors:
                neighbor = HumanNeighbor(
                    move_id=move_id,
                    ref_game_id=neighbor_data["ref_game_id"],
                    ref_ply=neighbor_data["ref_ply"],
                    similarity=neighbor_data["similarity"],
                    human_choice_san=neighbor_data["human_choice_san"],
                    meta=neighbor_data["meta"],
                )
                
                db.add(neighbor)
                saved_count += 1
            
            db.commit()
            return saved_count
            
        except Exception as e:
            db.rollback()
            print(f"Error saving neighbors: {e}")
            return 0
        finally:
            db.close()

