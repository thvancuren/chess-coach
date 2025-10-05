'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { Sword, Settings, Play, Pause, RotateCcw, Bot, User } from 'lucide-react'
import { toast } from 'react-hot-toast'
import ChessBoard from '@/components/ChessBoard'

interface SparringSession {
  session_id: string
  username: string
  difficulty: number
  style_hints: any
  created_at: string
}

export default function SparringPage() {
  const searchParams = useSearchParams()
  const username = searchParams.get('username') || ''
  
  const [session, setSession] = useState<SparringSession | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [difficulty, setDifficulty] = useState(3)
  const [currentPosition, setCurrentPosition] = useState('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
  const [gameHistory, setGameHistory] = useState<string[]>([])
  const [isPlayerTurn, setIsPlayerTurn] = useState(true)
  const [isGameActive, setIsGameActive] = useState(false)

  const handleCreateSession = async () => {
    if (!username) {
      toast.error('Please provide a username')
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/spar/bot/new`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          difficulty,
          style_hints: {}
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setSession(data)
        setIsGameActive(true)
        toast.success('Sparring session created!')
      } else {
        throw new Error('Failed to create session')
      }
    } catch (error) {
      toast.error('Failed to create sparring session')
    } finally {
      setIsLoading(false)
    }
  }

  const handleMove = async (moveIndex: number) => {
    if (!session || !isPlayerTurn || !isGameActive) return

    try {
      // For sparring, we'll use a mock move based on the moveIndex
      const mockMove = `move${moveIndex}`
      
      // Add move to history
      setGameHistory(prev => [...prev, mockMove])
      
      // Update position (simplified - in real implementation, this would be more complex)
      const newPosition = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1' // Mock position
      setCurrentPosition(newPosition)
      
      // Switch to bot's turn
      setIsPlayerTurn(false)
      
      // Simulate bot thinking and response
      setTimeout(() => {
        const botMove = 'e5' // Mock bot move
        setGameHistory(prev => [...prev, botMove])
        setCurrentPosition('rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2') // Mock position
        setIsPlayerTurn(true)
        toast.success(`Bot played: ${botMove}`)
      }, 1000)
      
    } catch (error) {
      toast.error('Invalid move')
    }
  }

  const handleReset = () => {
    setCurrentPosition('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    setGameHistory([])
    setIsPlayerTurn(true)
    setIsGameActive(false)
    setSession(null)
  }

  const getDifficultyText = (level: number) => {
    switch (level) {
      case 1: return 'Beginner (800-1000)'
      case 2: return 'Novice (1000-1200)'
      case 3: return 'Intermediate (1200-1400)'
      case 4: return 'Advanced (1400-1600)'
      case 5: return 'Expert (1600+)'
      default: return 'Intermediate'
    }
  }

  const getDifficultyColor = (level: number) => {
    switch (level) {
      case 1: return 'bg-green-100 text-green-800'
      case 2: return 'bg-blue-100 text-blue-800'
      case 3: return 'bg-yellow-100 text-yellow-800'
      case 4: return 'bg-orange-100 text-orange-800'
      case 5: return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">
          Sparring Bot
        </h1>
        <p className="text-slate-600">
          Practice against an AI opponent with adjustable difficulty
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-slate-900">
                {session ? `Sparring Session - ${getDifficultyText(difficulty)}` : 'Create New Session'}
              </h2>
              {session && (
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded text-xs ${getDifficultyColor(difficulty)}`}>
                    {getDifficultyText(difficulty)}
                  </span>
                </div>
              )}
            </div>

            {!session ? (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Difficulty Level
                  </label>
                  <div className="grid grid-cols-5 gap-2">
                    {[1, 2, 3, 4, 5].map((level) => (
                      <button
                        key={level}
                        onClick={() => setDifficulty(level)}
                        className={`p-3 rounded-lg text-sm font-medium ${
                          difficulty === level
                            ? 'bg-blue-600 text-white'
                            : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                        }`}
                      >
                        {level}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-slate-500 mt-2">
                    {getDifficultyText(difficulty)}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Style Hints (Optional)
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <label className="flex items-center space-x-2">
                      <input type="checkbox" className="rounded" />
                      <span className="text-sm">Aggressive</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input type="checkbox" className="rounded" />
                      <span className="text-sm">Positional</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input type="checkbox" className="rounded" />
                      <span className="text-sm">Tactical</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input type="checkbox" className="rounded" />
                      <span className="text-sm">Defensive</span>
                    </label>
                  </div>
                </div>

                <button
                  onClick={handleCreateSession}
                  disabled={isLoading}
                  className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Creating Session...</span>
                    </>
                  ) : (
                    <>
                      <Sword size={20} />
                      <span>Start Sparring</span>
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="flex justify-center">
                  <ChessBoard
                    position={currentPosition}
                    onMoveClick={handleMove}
                    currentMove={gameHistory.length}
                    totalMoves={gameHistory.length + 1}
                  />
                </div>

                <div className="flex justify-center space-x-4">
                  <button
                    onClick={handleReset}
                    className="bg-slate-600 text-white px-4 py-2 rounded-lg hover:bg-slate-700 flex items-center space-x-2"
                  >
                    <RotateCcw size={16} />
                    <span>New Game</span>
                  </button>
                </div>

                <div className="text-center">
                  <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-lg ${
                    isPlayerTurn ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-600'
                  }`}>
                    {isPlayerTurn ? <User size={16} /> : <Bot size={16} />}
                    <span>
                      {isPlayerTurn ? 'Your turn' : 'Bot is thinking...'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Game Info</h2>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Moves:</span>
                <span className="font-medium">{gameHistory.length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Status:</span>
                <span className="font-medium">
                  {isGameActive ? (isPlayerTurn ? 'Your Turn' : 'Bot\'s Turn') : 'Not Started'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Difficulty:</span>
                <span className="font-medium">{getDifficultyText(difficulty)}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Move History</h2>
            <div className="max-h-64 overflow-y-auto">
              {gameHistory.length === 0 ? (
                <p className="text-sm text-slate-500">No moves yet</p>
              ) : (
                <div className="space-y-1">
                  {gameHistory.map((move, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between text-sm p-2 bg-slate-50 rounded"
                    >
                      <span className="font-medium">{Math.ceil((index + 1) / 2)}.</span>
                      <span className="font-mono">{move}</span>
                      <span className="text-slate-500">
                        {index % 2 === 0 ? 'White' : 'Black'}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Tips</h2>
            <div className="space-y-2 text-sm text-slate-600">
              <p>&bull; The bot will adapt to your playing style</p>
              <p>&bull; Higher difficulty means stronger play</p>
              <p>&bull; Use this to practice specific openings</p>
              <p>&bull; Analyze your games afterward</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

