"""Stockfish UCI engine integration service."""

import io
import os
from typing import Any, Dict, List, Optional

import chess
import chess.engine
import chess.pgn

from app.models import Move, MistakeType, Side


class StockfishService:
    """Service for running Stockfish analysis on chess positions."""

    def __init__(self, stockfish_path: Optional[str] = None, depth: int = 20):
        self.stockfish_path = stockfish_path or os.getenv("STOCKFISH_PATH", "stockfish")
        self.depth = depth or int(os.getenv("ANALYSIS_DEPTH", "20"))
        self.engine: Optional[chess.engine.SimpleEngine] = None

    def __enter__(self):
        """Context manager entry."""
        self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.engine:
            self.engine.quit()

    def analyze_game(self, pgn: str, _username: str) -> List[Dict[str, Any]]:
        """Analyze a complete game and return move evaluations."""
        if self.engine is None:
            raise RuntimeError("Stockfish engine is not initialised. Use the service as a context manager.")

        moves_data: List[Dict[str, Any]] = []

        try:
            game = chess.pgn.read_game(io.StringIO(pgn))
            if not game:
                return moves_data

            board = game.board()
            ply = 0

            for move in game.mainline_moves():
                ply += 1
                side_to_move = board.turn
                info_before = self.engine.analyse(board, chess.engine.Limit(depth=self.depth))
                score_before = info_before.get("score")
                eval_before = self._convert_eval(score_before, side_to_move) if score_before else 0

                pv_moves = info_before.get("pv", [])
                best_move_uci = pv_moves[0].uci() if pv_moves else None
                pv_san = self._uci_to_san_list(board, pv_moves[:6]) if pv_moves else None
                if pv_san == "":
                    pv_san = None

                try:
                    san_notation = board.san(move)
                except ValueError:
                    san_notation = move.uci()

                board.push(move)
                info_after = self.engine.analyse(board, chess.engine.Limit(depth=self.depth))
                score_after = info_after.get("score")
                eval_after_mover = self._convert_eval(score_after, side_to_move) if score_after else eval_before
                eval_after_board = self._convert_eval(score_after, board.turn) if score_after else eval_after_mover
                eval_swing = eval_after_mover - eval_before

                mistake_tag = self._classify_mistake(eval_swing)

                pov_color = chess.WHITE if side_to_move else chess.BLACK
                mate_info = score_after.pov(pov_color).mate() if score_after else None

                move_data = {
                    "ply": ply,
                    "fen": board.fen(),
                    "san": san_notation,
                    "side": (Side.WHITE if side_to_move else Side.BLACK).value,
                    "sf_eval_cp": eval_after_board,
                    "sf_mate": mate_info,
                    "sf_bestmove_uci": best_move_uci,
                    "sf_pv": pv_san,
                    "mistake_tag": mistake_tag.value,
                }

                moves_data.append(move_data)

            return moves_data

        except (chess.engine.EngineError, chess.engine.EngineTerminatedError, ValueError) as exc:
            print(f"Error analyzing game: {exc}")
            return moves_data

    def _convert_eval(self, score: chess.engine.Score, perspective_white: bool) -> int:
        """Convert Stockfish score to centipawns from the mover's perspective."""
        pov_color = chess.WHITE if perspective_white else chess.BLACK
        score_pov = score.pov(pov_color)

        mate_score = score_pov.mate()
        if mate_score is not None:
            return 10000 - mate_score * 100 if mate_score > 0 else -10000 - mate_score * 100

        return int(score_pov.score(mate_score=10000))

    def _classify_mistake(self, eval_swing: int) -> MistakeType:
        """Classify mistake based on evaluation swing."""
        abs_swing = abs(eval_swing)

        if abs_swing >= 200:
            return MistakeType.BLUNDER
        if abs_swing >= 150:
            return MistakeType.MISTAKE
        if abs_swing >= 90:
            return MistakeType.INACCURACY
        return MistakeType.NONE

    def _uci_to_san_list(self, board: chess.Board, uci_moves: List[chess.Move]) -> str:
        """Convert UCI moves to SAN notation list."""
        san_moves: List[str] = []
        temp_board = board.copy()

        for move in uci_moves:
            try:
                san_moves.append(temp_board.san(move))
                temp_board.push(move)
            except ValueError:
                break

        return " ".join(san_moves)

    def save_moves(self, game_id: str, moves_data: List[Dict[str, Any]]) -> int:
        """Save analyzed moves to database."""
        from app.db import SessionLocal
        import uuid

        print(f"Saving {len(moves_data)} moves for game {game_id}")
        db = SessionLocal()
        saved_count = 0

        try:
            for move_data in moves_data:
                move = Move(
                    game_id=uuid.UUID(game_id),
                    ply=move_data["ply"],
                    fen=move_data["fen"],
                    san=move_data["san"],
                    side=Side(move_data["side"]),
                    sf_eval_cp=move_data["sf_eval_cp"],
                    sf_mate=move_data["sf_mate"],
                    sf_bestmove_uci=move_data["sf_bestmove_uci"],
                    sf_pv=move_data["sf_pv"],
                    mistake_tag=MistakeType(move_data["mistake_tag"]),
                )

                db.add(move)
                saved_count += 1

            db.commit()
            print(f"Successfully saved {saved_count} moves for game {game_id}")
            return saved_count

        except Exception as exc:
            db.rollback()
            print(f"Error saving moves for game {game_id}: {exc}")
            import traceback
            traceback.print_exc()
            return 0
        finally:
            db.close()
