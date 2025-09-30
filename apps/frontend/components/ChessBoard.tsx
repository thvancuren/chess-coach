'use client'

import { useState, useEffect } from 'react'
import { Chess as ChessEngine } from 'chess.js'

interface ChessBoardProps {
  position: string
  onMoveClick?: (moveIndex: number) => void
  currentMove?: number
  totalMoves?: number
}

export default function ChessBoard({ 
  position, 
  onMoveClick, 
  currentMove = 0, 
  totalMoves = 0 
}: ChessBoardProps) {
  const [game, setGame] = useState(new ChessEngine())
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null)
  const [possibleMoves, setPossibleMoves] = useState<string[]>([])

  useEffect(() => {
    try {
      const newGame = new ChessEngine(position)
      setGame(newGame)
    } catch (error) {
      console.error('Invalid FEN position:', error)
    }
  }, [position])

  const handleSquareClick = (square: string) => {
    if (selectedSquare) {
      // Try to make a move
      try {
        const move = game.move({
          from: selectedSquare,
          to: square,
          promotion: 'q' // Always promote to queen for simplicity
        })
        
        if (move) {
          setSelectedSquare(null)
          setPossibleMoves([])
          // Notify parent component about the move
          if (onMoveClick && currentMove < totalMoves) {
            onMoveClick(currentMove + 1)
          }
        } else {
          // Invalid move, select new square
          setSelectedSquare(square)
          setPossibleMoves(getPossibleMoves(square))
        }
      } catch (error) {
        // Invalid move, select new square
        setSelectedSquare(square)
        setPossibleMoves(getPossibleMoves(square))
      }
    } else {
      // Select square
      setSelectedSquare(square)
      setPossibleMoves(getPossibleMoves(square))
    }
  }

  const getPossibleMoves = (square: string): string[] => {
    const moves = game.moves({ square: square as any, verbose: true })
    return moves.map((move: any) => move.to)
  }

  const getSquareColor = (square: string): string => {
    const file = square.charCodeAt(0) - 97
    const rank = parseInt(square[1]) - 1
    return (file + rank) % 2 === 0 ? 'bg-chess-light' : 'bg-chess-dark'
  }

  const getPieceSymbol = (piece: any): string => {
    if (!piece) return ''
    
    const symbols: { [key: string]: string } = {
      'wK': '♔', 'wQ': '♕', 'wR': '♖', 'wB': '♗', 'wN': '♘', 'wP': '♙',
      'bK': '♚', 'bQ': '♛', 'bR': '♜', 'bB': '♝', 'bN': '♞', 'bP': '♟'
    }
    
    return symbols[piece.color + piece.type.toUpperCase()] || ''
  }

  const renderSquare = (square: string) => {
    const piece = game.get(square as any)
    const isSelected = selectedSquare === square
    const isPossibleMove = possibleMoves.includes(square)
    
    return (
      <div
        key={square}
        className={`
          chess-square ${getSquareColor(square)}
          ${isSelected ? 'selected' : ''}
          ${isPossibleMove ? 'possible-move' : ''}
        `}
        onClick={() => handleSquareClick(square)}
      >
        {piece && (
          <span className="text-4xl">
            {getPieceSymbol(piece)}
          </span>
        )}
        {isPossibleMove && !piece && (
          <div className="w-3 h-3 bg-blue-500 rounded-full opacity-50"></div>
        )}
      </div>
    )
  }

  const renderBoard = () => {
    const squares = []
    for (let rank = 8; rank >= 1; rank--) {
      for (let file = 0; file < 8; file++) {
        const square = String.fromCharCode(97 + file) + rank
        squares.push(renderSquare(square))
      }
    }
    return squares
  }

  return (
    <div className="chess-board">
      <div className="grid grid-cols-8 border-2 border-slate-800">
        {renderBoard()}
      </div>
      <div className="mt-4 text-center text-sm text-slate-600">
        Move {currentMove} of {totalMoves}
      </div>
    </div>
  )
}

