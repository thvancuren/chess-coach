#!/usr/bin/env python3
"""Seed the database with demo data."""

import os
import sys
from datetime import datetime

# Add the backend to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend'))

from app.db import SessionLocal, create_tables
from app.models import Game, Move, MistakeType, Side, GameResult


def create_demo_data():
    """Create demo games and moves."""
    db = SessionLocal()
    
    try:
        # Create tables
        create_tables()
        
        # Create demo game
        game = Game(
            username="demo_user",
            site="chesscom",
            pgn="[Event \"Live Chess\"]\n[Site \"Chess.com\"]\n[Date \"2024.01.01\"]\n[White \"demo_user\"]\n[Black \"opponent\"]\n[Result \"1-0\"]\n[ECO \"A00\"]\n[Opening \"King's Pawn Game\"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7 11. c4 c6 12. cxb5 axb5 13. Nc3 Bb7 14. Bg5 b4 15. Nb1 h6 16. Bh4 c5 17. dxe5 Nxe4 18. Bxe7 Qxe7 19. exd6 Qf6 20. Nbd2 Nxd6 21. Nc4 Nxc4 22. Bxc4 Nb6 23. Ne5 Rae8 24. Bxf7+ Rxf7 25. Nxf7 Rxe1+ 26. Qxe1 Kxf7 27. Qe3 Qg5 28. Qxg5 hxg5 29. b3 Ke6 30. a3 Kd6 31. axb4 cxb4 32. Ra5 Nd5 33. f3 Bc8 34. Kf2 Bf5 35. Ra7 g6 36. Ra6+ Kc5 37. Ke1 Nf4 38. g3 Nxh3 39. Kd2 Kb5 40. Rd6 Kc5 41. Ra6 Nf2 42. g4 Bd3 43. Re6 1-0",
            json={"demo": True},
            eco="A00",
            opening="King's Pawn Game",
            result=GameResult.WHITE_WINS,
            time_control="10+0",
            white="demo_user",
            black="opponent",
            started_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        db.add(game)
        db.commit()
        
        # Create demo moves
        moves_data = [
            {"ply": 1, "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", "san": "e4", "side": "white", "sf_eval_cp": 20, "mistake_tag": "none"},
            {"ply": 2, "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2", "san": "e5", "side": "black", "sf_eval_cp": 15, "mistake_tag": "none"},
            {"ply": 3, "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKBNR b KQkq - 1 2", "san": "Nf3", "side": "white", "sf_eval_cp": 25, "mistake_tag": "none"},
        ]
        
        for move_data in moves_data:
            move = Move(
                game_id=game.id,
                ply=move_data["ply"],
                fen=move_data["fen"],
                san=move_data["san"],
                side=Side(move_data["side"]),
                sf_eval_cp=move_data["sf_eval_cp"],
                mistake_tag=MistakeType(move_data["mistake_tag"])
            )
            db.add(move)
        
        db.commit()
        print("Demo data created successfully!")
        
    except Exception as e:
        print(f"Error creating demo data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    create_demo_data()

