'use client'

import { useState, useEffect } from 'react'
import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'

interface ChessBoardProps {
  position: string
  onMoveClick?: (moveIndex: number) => void
  currentMove?: number
  totalMoves?: number
  lastMove?: { from: string; to: string } | null
  whitePlayer?: string
  blackPlayer?: string
}

export default function ChessBoard({
  position,
  onMoveClick,
  currentMove = 0,
  totalMoves = 0,
  lastMove = null,
  whitePlayer,
  blackPlayer
}: ChessBoardProps) {
  const [game, setGame] = useState(() => new Chess())

  useEffect(() => {
    try {
      console.log('ChessBoard position:', position)
      const newGame = new Chess(position)
      setGame(newGame)
    } catch (error) {
      console.error('Invalid FEN position:', error)
    }
  }, [position])

  const handleSquareClick = (square: string) => {
    // Handle move navigation when clicking squares
    if (onMoveClick && currentMove < totalMoves) {
      onMoveClick(currentMove + 1)
    }
  }

  const handlePieceDrop = (sourceSquare: string, targetSquare: string) => {
    // Handle piece movement for move navigation
    if (onMoveClick && currentMove < totalMoves) {
      onMoveClick(currentMove + 1)
      return true
    }
    return false
  }

  // Prepare highlighted squares for the last move
  const highlightedSquares = lastMove ? {
    [lastMove.from]: { backgroundColor: '#fbbf24' },
    [lastMove.to]: { backgroundColor: '#fbbf24' }
  } : {}

  try {
    return (
      <div className="chess-board">
        {/* Black player name (top) */}
        {blackPlayer && (
          <div className="text-center mb-2">
            <div className="bg-slate-800 text-white px-4 py-2 rounded-lg inline-block">
              <span className="font-medium">{blackPlayer}</span>
              <span className="ml-2 text-slate-300">(Black)</span>
            </div>
          </div>
        )}
        
        <div className="flex justify-center">
          <Chessboard
            position={position}
            onSquareClick={handleSquareClick}
            onPieceDrop={handlePieceDrop}
            customSquareStyles={highlightedSquares}
            boardWidth={600}
            showBoardNotation={true}
            animationDuration={200}
            areArrowsAllowed={false}
            arePiecesDraggable={false}
          />
        </div>
        
        {/* White player name (bottom) */}
        {whitePlayer && (
          <div className="text-center mt-2">
            <div className="bg-slate-100 text-slate-800 px-4 py-2 rounded-lg inline-block border">
              <span className="font-medium">{whitePlayer}</span>
              <span className="ml-2 text-slate-600">(White)</span>
            </div>
          </div>
        )}
        
        <div className="mt-4 text-center text-sm text-slate-600">
          Move {currentMove} of {totalMoves}
        </div>
      </div>
    )
  } catch (error) {
    console.error('ChessBoard render error:', error)
    return (
      <div className="chess-board">
        <div className="flex justify-center items-center h-96 bg-slate-100 rounded-lg">
          <div className="text-center">
            <p className="text-slate-600 mb-2">Chess Board Error</p>
            <p className="text-sm text-slate-500">Position: {position}</p>
            <p className="text-sm text-slate-500">Error: {error instanceof Error ? error.message : 'Unknown error'}</p>
          </div>
        </div>
        <div className="mt-4 text-center text-sm text-slate-600">
          Move {currentMove} of {totalMoves}
        </div>
      </div>
    )
  }
}

