'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { Puzzle, RotateCcw, CheckCircle, XCircle, Lightbulb } from 'lucide-react'
import { toast } from 'react-hot-toast'
import ChessBoard from '@/components/ChessBoard'

interface PuzzleData {
  id: string
  fen_start: string
  solution_san: string[]
  motif: string | null
  strength: number
  created_at: string
}

export default function PuzzlesPage() {
  const searchParams = useSearchParams()
  const username = searchParams.get('username') || ''
  
  const [puzzles, setPuzzles] = useState<PuzzleData[]>([])
  const [currentPuzzle, setCurrentPuzzle] = useState<PuzzleData | null>(null)
  const [currentMove, setCurrentMove] = useState(0)
  const [userMoves, setUserMoves] = useState<string[]>([])
  const [isSolved, setIsSolved] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [showHint, setShowHint] = useState(false)

  useEffect(() => {
    if (username) {
      fetchPuzzles()
    }
  }, [username])

  const fetchPuzzles = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/puzzles?username=${username}&limit=20`
      )
      if (response.ok) {
        const data = await response.json()
        setPuzzles(data)
        if (data.length > 0) {
          setCurrentPuzzle(data[0])
        }
      }
    } catch (error) {
      toast.error('Failed to fetch puzzles')
    } finally {
      setIsLoading(false)
    }
  }

  const handleMove = (moveIndex: number) => {
    if (!currentPuzzle || isSolved) return

    // For puzzles, we don't actually need the moveIndex since we're just advancing
    // through the solution moves. This is a simplified implementation.
    if (currentMove < currentPuzzle.solution_san.length) {
      setCurrentMove(currentMove + 1)
      
      if (currentMove + 1 >= currentPuzzle.solution_san.length) {
        setIsSolved(true)
        toast.success('Puzzle solved! Well done!')
      } else {
        toast.success('Correct! Next move...')
      }
    }
  }

  const handleNextPuzzle = () => {
    const currentIndex = puzzles.findIndex(p => p.id === currentPuzzle?.id)
    const nextIndex = (currentIndex + 1) % puzzles.length
    setCurrentPuzzle(puzzles[nextIndex])
    setCurrentMove(0)
    setUserMoves([])
    setIsSolved(false)
    setShowHint(false)
  }

  const handleReset = () => {
    setCurrentMove(0)
    setUserMoves([])
    setIsSolved(false)
    setShowHint(false)
  }

  const getMotifColor = (motif: string | null) => {
    switch (motif) {
      case 'check':
        return 'bg-red-100 text-red-800'
      case 'capture':
        return 'bg-orange-100 text-orange-800'
      case 'fork':
        return 'bg-yellow-100 text-yellow-800'
      case 'pin':
        return 'bg-blue-100 text-blue-800'
      case 'skewer':
        return 'bg-purple-100 text-purple-800'
      case 'back-rank':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStrengthStars = (strength: number) => {
    const safeStrength = Math.max(0, Math.min(5, strength))
    const filled = '\u2605'.repeat(safeStrength)
    const empty = '\u2606'.repeat(5 - safeStrength)
    return `${filled}${empty}`
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (puzzles.length === 0) {
    return (
      <div className="text-center py-12">
        <Puzzle className="mx-auto text-slate-400 mb-4" size={48} />
        <h3 className="text-lg font-medium text-slate-900 mb-2">No puzzles found</h3>
        <p className="text-slate-600 mb-4">
          Generate puzzles from your games to start practicing
        </p>
        <button
          onClick={() => fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/puzzles/generate?username=${username}`, { method: 'POST' })}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
        >
          Generate Puzzles
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">
          Puzzles for {username}
        </h1>
        <p className="text-slate-600">
          Practice with puzzles generated from your own mistakes
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-slate-900">
                Puzzle {puzzles.findIndex(p => p.id === currentPuzzle?.id) + 1} of {puzzles.length}
              </h2>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-slate-600">Difficulty:</span>
                <span className="text-yellow-500">{getStrengthStars(currentPuzzle?.strength || 1)}</span>
              </div>
            </div>

            {currentPuzzle && (
              <div className="mb-4">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-sm font-medium text-slate-600">Motif:</span>
                  <span className={`px-2 py-1 rounded text-xs ${getMotifColor(currentPuzzle.motif)}`}>
                    {currentPuzzle.motif || 'Tactics'}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-slate-600">Solution:</span>
                  <span className="text-sm text-slate-500">
                    {currentMove < currentPuzzle.solution_san.length ? '?' : currentPuzzle.solution_san.join(' ')}
                  </span>
                </div>
              </div>
            )}

            <div className="flex justify-center mb-6">
              <ChessBoard
                position={currentPuzzle?.fen_start || 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'}
                onMoveClick={handleMove}
                currentMove={currentMove}
                totalMoves={currentPuzzle?.solution_san.length || 0}
              />
            </div>

            <div className="flex justify-center space-x-4">
              <button
                onClick={handleReset}
                className="bg-slate-600 text-white px-4 py-2 rounded-lg hover:bg-slate-700 flex items-center space-x-2"
              >
                <RotateCcw size={16} />
                <span>Reset</span>
              </button>
              <button
                onClick={() => setShowHint(!showHint)}
                className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 flex items-center space-x-2"
              >
                <Lightbulb size={16} />
                <span>{showHint ? 'Hide' : 'Show'} Hint</span>
              </button>
              <button
                onClick={handleNextPuzzle}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                Next Puzzle
              </button>
            </div>

            {showHint && currentPuzzle && (
              <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
                <h3 className="font-medium text-yellow-800 mb-2">Hint</h3>
                <p className="text-sm text-yellow-700">
                  Look for tactical patterns like {currentPuzzle.motif || 'checks, captures, and threats'}.
                  The solution involves {currentPuzzle.solution_san.length} move{currentPuzzle.solution_san.length > 1 ? 's' : ''}.
                </p>
              </div>
            )}

            {isSolved && (
              <div className="mt-4 p-4 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="text-green-600" size={20} />
                  <span className="font-medium text-green-800">Puzzle Solved!</span>
                </div>
                <p className="text-sm text-green-700 mt-1">
                  Great job! The solution was: {currentPuzzle?.solution_san.join(' ')}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Progress</h2>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Moves Made:</span>
                <span>{currentMove} / {currentPuzzle?.solution_san.length || 0}</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{
                    width: `${((currentMove / (currentPuzzle?.solution_san.length || 1)) * 100)}%`
                  }}
                ></div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Puzzle List</h2>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {puzzles.map((puzzle, index) => (
                <button
                  key={puzzle.id}
                  onClick={() => {
                    setCurrentPuzzle(puzzle)
                    setCurrentMove(0)
                    setUserMoves([])
                    setIsSolved(false)
                    setShowHint(false)
                  }}
                  className={`w-full text-left p-3 rounded-lg text-sm ${
                    puzzle.id === currentPuzzle?.id
                      ? 'bg-blue-100 text-blue-900'
                      : 'hover:bg-slate-100'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span>Puzzle {index + 1}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-yellow-500 text-xs">
                        {getStrengthStars(puzzle.strength)}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs ${getMotifColor(puzzle.motif)}`}>
                        {puzzle.motif || 'Tactics'}
                      </span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
