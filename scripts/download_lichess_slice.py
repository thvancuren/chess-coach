#!/usr/bin/env python3
"""Download and process a slice of the Lichess database for human reference."""

import os
import sys
import requests
import sqlite3
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import chess
import chess.pgn
from datetime import datetime

# Add the backend to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend'))

from app.services.human_index import HumanIndexService


def download_lichess_month(year: int, month: int, output_dir: str = "/data") -> str:
    """Download a monthly Lichess database file."""
    url = f"https://database.lichess.org/standard/lichess_db_standard_rated_{year:04d}-{month:02d}.pgn.zst"
    
    output_path = os.path.join(output_dir, f"lichess_{year:04d}-{month:02d}.pgn.zst")
    
    print(f"Downloading {url}...")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"Downloaded to {output_path}")
    return output_path


def process_lichess_file(file_path: str, sample_size: int = 10000) -> List[Dict[str, Any]]:
    """Process Lichess PGN file and extract GM games."""
    print(f"Processing {file_path}...")
    
    # This is a simplified implementation
    # In practice, you would:
    # 1. Decompress the .zst file
    # 2. Parse PGN games
    # 3. Filter for GM games (ELO > 2500)
    # 4. Extract positions and features
    
    games = []
    
    # Mock data for demonstration
    for i in range(min(sample_size, 1000)):
        game = {
            'id': f'lichess_{i}',
            'white': f'GM_Player_{i}',
            'black': f'GM_Player_{i+1}',
            'result': '1-0' if i % 2 == 0 else '0-1',
            'eco': 'A00',
            'positions': [
                {
                    'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                    'ply': 0,
                    'human_choice': 'e4',
                    'eval_band': 0
                }
            ]
        }
        games.append(game)
    
    print(f"Processed {len(games)} games")
    return games


def build_human_index(games: List[Dict[str, Any]], index_path: str) -> None:
    """Build the human reference index."""
    print(f"Building human index at {index_path}...")
    
    # Create SQLite database
    conn = sqlite3.connect(index_path)
    cursor = conn.cursor()
    
    # Create table
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
    
    # Insert positions
    for game in games:
        for pos in game['positions']:
            # Calculate features
            board = chess.Board(pos['fen'])
            eco = 'A00'  # Simplified
            side = 0 if board.turn else 1
            pawn_hash = hashlib.md5(pos['fen'].encode()).hexdigest()[:8]
            eval_band = pos['eval_band']
            piece_activity = 10.0  # Simplified
            
            cursor.execute("""
                INSERT INTO human_positions 
                (fen, eco, side, pawn_hash, eval_band, piece_activity, human_choice_san, game_id, ply, meta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pos['fen'],
                eco,
                side,
                pawn_hash,
                eval_band,
                piece_activity,
                pos['human_choice'],
                game['id'],
                pos['ply'],
                '{}'
            ))
    
    conn.commit()
    conn.close()
    
    print(f"Human index built with {len(games)} games")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download and process Lichess database slice')
    parser.add_argument('--year', type=int, default=2023, help='Year to download')
    parser.add_argument('--month', type=int, default=1, help='Month to download')
    parser.add_argument('--sample-size', type=int, default=10000, help='Number of games to sample')
    parser.add_argument('--output-dir', default='/data', help='Output directory')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        # Download file
        file_path = download_lichess_month(args.year, args.month, args.output_dir)
        
        # Process games
        games = process_lichess_file(file_path, args.sample_size)
        
        # Build index
        index_path = os.path.join(args.output_dir, 'human_index.sqlite')
        build_human_index(games, index_path)
        
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

