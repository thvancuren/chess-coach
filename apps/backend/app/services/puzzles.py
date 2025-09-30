"""Puzzle generation service from user blunders."""

import chess
import chess.pgn
from typing import List, Dict, Any, Optional
from app.models import Puzzle, Move, MistakeType
from app.db import SessionLocal


class PuzzleService:
    """Service for generating puzzles from user mistakes."""
    
    def __init__(self):
        pass
    
    def generate_puzzles_from_blunders(self, username: str) -> int:
        """Generate puzzles from all blunders for a user."""
        db = SessionLocal()
        generated_count = 0
        
        try:
            # Find all blunders for the user
            blunders = db.query(Move).join(Move.game).filter(
                Move.mistake_tag == MistakeType.BLUNDER,
                Move.game.has(username=username)
            ).all()
            
            for blunder in blunders:
                # Skip if puzzle already exists for this move
                existing_puzzle = db.query(Puzzle).filter(
                    Puzzle.source_move_id == blunder.id
                ).first()
                
                if existing_puzzle:
                    continue
                
                # Generate puzzle from this blunder
                puzzle_data = self._create_puzzle_from_blunder(blunder)
                if puzzle_data:
                    puzzle = Puzzle(
                        source_move_id=blunder.id,
                        game_id=blunder.game_id,
                        fen_start=puzzle_data["fen_start"],
                        solution_san=puzzle_data["solution_san"],
                        motif=puzzle_data["motif"],
                        strength=puzzle_data["strength"],
                    )
                    
                    db.add(puzzle)
                    generated_count += 1
            
            db.commit()
            return generated_count
            
        except Exception as e:
            db.rollback()
            print(f"Error generating puzzles: {e}")
            return 0
        finally:
            db.close()
    
    def _create_puzzle_from_blunder(self, blunder: Move) -> Optional[Dict[str, Any]]:
        """Create a puzzle from a blunder move."""
        try:
            # Get the position one move before the blunder
            board = chess.Board(blunder.fen)
            
            # The puzzle starts from the position before the blunder
            # We need to go back one move to get the starting position
            if blunder.ply > 1:
                # Find the previous move
                prev_move = self._get_previous_move(blunder)
                if prev_move:
                    # Set up board from previous position
                    board = chess.Board(prev_move.fen)
                else:
                    return None
            
            # The solution is the best move (from Stockfish analysis)
            if not blunder.sf_bestmove_uci:
                return None
            
            best_move_uci = blunder.sf_bestmove_uci
            best_move = chess.Move.from_uci(best_move_uci)
            
            if best_move not in board.legal_moves:
                return None
            
            # Convert to SAN
            best_move_san = board.san(best_move)
            
            # Generate full solution (principal variation)
            solution_san = self._generate_solution_sequence(board, blunder)
            
            # Determine motif
            motif = self._identify_motif(board, best_move, blunder)
            
            # Determine strength (1-5 based on complexity)
            strength = self._calculate_strength(board, best_move, blunder)
            
            return {
                "fen_start": board.fen(),
                "solution_san": solution_san,
                "motif": motif,
                "strength": strength,
            }
            
        except Exception as e:
            print(f"Error creating puzzle from blunder: {e}")
            return None
    
    def _get_previous_move(self, current_move: Move) -> Optional[Move]:
        """Get the previous move in the game."""
        from app.db import SessionLocal
        
        db = SessionLocal()
        try:
            prev_move = db.query(Move).filter(
                Move.game_id == current_move.game_id,
                Move.ply == current_move.ply - 1
            ).first()
            return prev_move
        finally:
            db.close()
    
    def _generate_solution_sequence(self, board: chess.Board, blunder: Move) -> List[str]:
        """Generate the solution sequence from the principal variation."""
        if not blunder.sf_pv:
            return []
        
        # Parse the PV string into individual moves
        pv_moves = blunder.sf_pv.split()
        solution = []
        
        temp_board = board.copy()
        for move_san in pv_moves[:6]:  # Limit to first 6 moves
            try:
                move = temp_board.parse_san(move_san)
                if move in temp_board.legal_moves:
                    solution.append(move_san)
                    temp_board.push(move)
                else:
                    break
            except:
                break
        
        return solution
    
    def _identify_motif(self, board: chess.Board, best_move: chess.Move, 
                       blunder: Move) -> str:
        """Identify the tactical motif of the puzzle."""
        # Check for common tactical patterns
        
        # Check if it's a check
        temp_board = board.copy()
        temp_board.push(best_move)
        if temp_board.is_check():
            return "check"
        
        # Check if it's a capture
        if board.is_capture(best_move):
            return "capture"
        
        # Check if it's a fork
        if self._is_fork(board, best_move):
            return "fork"
        
        # Check if it's a pin
        if self._is_pin(board, best_move):
            return "pin"
        
        # Check if it's a skewer
        if self._is_skewer(board, best_move):
            return "skewer"
        
        # Check if it's a back-rank mate
        if self._is_back_rank_mate(board, best_move):
            return "back-rank"
        
        # Check if it's a discovered attack
        if self._is_discovered_attack(board, best_move):
            return "discovered-attack"
        
        return "tactics"
    
    def _is_fork(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if move creates a fork."""
        temp_board = board.copy()
        temp_board.push(move)
        
        # Check if the moved piece attacks multiple enemy pieces
        piece_square = move.to_square
        piece = temp_board.piece_at(piece_square)
        
        if not piece:
            return False
        
        attacked_pieces = 0
        for square in chess.SQUARES:
            if (temp_board.piece_at(square) and 
                temp_board.piece_at(square).color != piece.color and
                temp_board.is_attacked_by(piece.color, square)):
                attacked_pieces += 1
        
        return attacked_pieces >= 2
    
    def _is_pin(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if move creates a pin."""
        # This is a simplified check - in practice, you'd need more sophisticated logic
        return False
    
    def _is_skewer(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if move creates a skewer."""
        # This is a simplified check - in practice, you'd need more sophisticated logic
        return False
    
    def _is_back_rank_mate(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if move creates a back-rank mate threat."""
        temp_board = board.copy()
        temp_board.push(move)
        
        # Check if the move creates a check that could lead to back-rank mate
        if temp_board.is_check():
            # Check if the king is trapped on the back rank
            king_square = temp_board.king(not temp_board.turn)
            if king_square:
                rank = chess.square_rank(king_square)
                if rank in [0, 7]:  # Back rank
                    return True
        
        return False
    
    def _is_discovered_attack(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if move creates a discovered attack."""
        # This is a simplified check - in practice, you'd need more sophisticated logic
        return False
    
    def _calculate_strength(self, board: chess.Board, best_move: chess.Move, 
                          blunder: Move) -> int:
        """Calculate puzzle strength (1-5) based on complexity."""
        # Base strength on evaluation swing
        eval_swing = abs(blunder.sf_eval_cp or 0)
        
        if eval_swing >= 500:
            return 5
        elif eval_swing >= 300:
            return 4
        elif eval_swing >= 200:
            return 3
        elif eval_swing >= 100:
            return 2
        else:
            return 1

