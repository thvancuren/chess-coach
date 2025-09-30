'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Play, Pause, RotateCcw, BarChart3 } from 'lucide-react'
import ChessBoard from '@/components/ChessBoard'
import EvalGraph from '@/components/EvalGraph'

interface Move {
  id: string
  ply: number
  fen: string
  san: string
  side: string
  time_left_ms: number | null
  sf_eval_cp: number | null
  sf_mate: number | null
  sf_bestmove_uci: string | null
  sf_pv: string | null
  mistake_tag: string
}

interface GameDetail {
  id: string
  username: string
  site: string
  eco: string | null
  opening: string | null
  result: string | null
  time_control: string | null
  white: string | null
  black: string | null
  started_at: string | null
  created_at: string
  pgn: string
  moves: Move[]
  features: any
}

export default function GameDetailPage() {
  const params = useParams()
  const gameId = params.id as string
  
  const [game, setGame] = useState<GameDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [currentMove, setCurrentMove] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)

  useEffect(() => {
    fetchGame()
  }, [gameId])

  const fetchGame = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/games/${gameId}`
      )
      if (response.ok) {
        const data = await response.json()
        setGame(data)
      }
    } catch (error) {
      console.error('Failed to fetch game:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleMoveClick = (moveIndex: number) => {
    setCurrentMove(moveIndex)
  }

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying)
  }

  const handleReset = () => {
    setCurrentMove(0)
    setIsPlaying(false)
  }

  const getEvalData = () => {
    if (!game) return []
    return game.moves.map((move, index) => ({
      move: index + 1,
      eval: move.sf_eval_cp || 0,
      mate: move.sf_mate,
      mistake: move.mistake_tag
    }))
  }

  const getCurrentPosition = () => {
    if (!game || currentMove === 0) {
      return 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    }
    return game.moves[currentMove - 1]?.fen || 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
  }

  const getCurrentMove = () => {
    if (!game || currentMove === 0) return null
    return game.moves[currentMove - 1]
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!game) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-slate-900 mb-2">Game not found</h3>
        <Link
          href="/games"
          className="text-blue-600 hover:text-blue-900"
        >
          Back to Games
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <Link
          href="/games"
          className="inline-flex items-center text-slate-600 hover:text-slate-900 mb-4"
        >
          <ArrowLeft className="mr-2" size={16} />
          Back to Games
        </Link>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 mb-2">
                {game.white} vs {game.black}
              </h1>
              <div className="flex items-center space-x-4 text-sm text-slate-600">
                <span>{game.eco || 'N/A'}</span>
                <span>•</span>
                <span>{game.opening || 'Unknown Opening'}</span>
                <span>•</span>
                <span>{game.time_control || 'N/A'}</span>
                <span>•</span>
                <span>{game.result || 'Unknown'}</span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handlePlayPause}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
              >
                {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                <span>{isPlaying ? 'Pause' : 'Play'}</span>
              </button>
              <button
                onClick={handleReset}
                className="bg-slate-600 text-white px-4 py-2 rounded-lg hover:bg-slate-700 flex items-center space-x-2"
              >
                <RotateCcw size={16} />
                <span>Reset</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Chess Board</h2>
            <div className="flex justify-center">
              <ChessBoard
                position={getCurrentPosition()}
                onMoveClick={handleMoveClick}
                currentMove={currentMove}
                totalMoves={game.moves.length}
              />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Evaluation Graph</h2>
            <EvalGraph data={getEvalData()} currentMove={currentMove} />
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Move List</h2>
            <div className="max-h-96 overflow-y-auto">
              <div className="grid grid-cols-2 gap-2">
                {game.moves.map((move, index) => (
                  <button
                    key={move.id}
                    onClick={() => handleMoveClick(index + 1)}
                    className={`p-2 text-left rounded-lg text-sm ${
                      currentMove === index + 1
                        ? 'bg-blue-100 text-blue-900'
                        : 'hover:bg-slate-100'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-medium">
                        {Math.ceil((index + 1) / 2)}. {index % 2 === 0 ? '' : '...'}
                        {move.san}
                      </span>
                      <div className="flex items-center space-x-1">
                        {move.sf_eval_cp && (
                          <span className="text-xs text-slate-500">
                            {move.sf_eval_cp > 0 ? '+' : ''}
                            {(move.sf_eval_cp / 100).toFixed(1)}
                          </span>
                        )}
                        {move.mistake_tag !== 'none' && (
                          <span className={`text-xs px-1 py-0.5 rounded ${
                            move.mistake_tag === 'blunder' ? 'bg-red-100 text-red-800' :
                            move.mistake_tag === 'mistake' ? 'bg-orange-100 text-orange-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {move.mistake_tag}
                          </span>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {getCurrentMove() && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Current Move Analysis</h2>
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-slate-600">Move:</span>
                  <span className="ml-2 font-mono">{getCurrentMove()?.san}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-slate-600">Evaluation:</span>
                  <span className="ml-2 font-mono">
                    {(() => {
                      const move = getCurrentMove();
                      return move?.sf_eval_cp ? 
                        `${move.sf_eval_cp > 0 ? '+' : ''}${(move.sf_eval_cp / 100).toFixed(1)}` :
                        'N/A';
                    })()}
                  </span>
                </div>
                <div>
                  <span className="text-sm font-medium text-slate-600">Best Move:</span>
                  <span className="ml-2 font-mono">{getCurrentMove()?.sf_bestmove_uci || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-slate-600">Mistake Level:</span>
                  <span className={`ml-2 px-2 py-1 rounded text-xs ${
                    getCurrentMove()?.mistake_tag === 'blunder' ? 'bg-red-100 text-red-800' :
                    getCurrentMove()?.mistake_tag === 'mistake' ? 'bg-orange-100 text-orange-800' :
                    getCurrentMove()?.mistake_tag === 'inacc' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {getCurrentMove()?.mistake_tag || 'none'}
                  </span>
                </div>
                {getCurrentMove()?.sf_pv && (
                  <div>
                    <span className="text-sm font-medium text-slate-600">Principal Variation:</span>
                    <div className="mt-1 font-mono text-sm bg-slate-100 p-2 rounded">
                      {getCurrentMove()?.sf_pv}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

