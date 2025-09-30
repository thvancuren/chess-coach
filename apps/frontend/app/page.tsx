'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'react-hot-toast'
import { Gamepad2, User, Download, BarChart3, Upload, FileText, Square } from 'lucide-react'
import ChessBoard from '@/components/ChessBoard'

export default function HomePage() {
  const [username, setUsername] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [pgnText, setPgnText] = useState('')
  const [isUploadingPgn, setIsUploadingPgn] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  const handleImport = async () => {
    if (!username.trim()) {
      toast.error('Please enter a Chess.com username')
      return
    }

    setIsLoading(true)
    try {
      // Import games
      const importResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/import/chesscom`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username.trim() }),
      })

      if (!importResponse.ok) {
        throw new Error('Failed to import games')
      }

      toast.success('Games imported successfully! Starting analysis...')

      // Start analysis
      const analysisResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/analyze/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username.trim() }),
      })

      if (!analysisResponse.ok) {
        throw new Error('Failed to start analysis')
      }

      toast.success('Analysis started! Redirecting to games...')
      router.push(`/games?username=${username.trim()}`)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const handlePgnFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.pgn')) {
      toast.error('Please select a .pgn file')
      return
    }

    if (!username.trim()) {
      toast.error('Please enter a username first')
      return
    }

    setIsUploadingPgn(true)
    try {
      const formData = new FormData()
      formData.append('username', username.trim())
      formData.append('file', file)

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/pgn/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to upload PGN file')
      }

      const result = await response.json()
      toast.success(`Successfully uploaded ${result.saved_games} games from PGN file!`)
      
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      // Redirect to games page
      router.push(`/games?username=${username.trim()}`)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to upload PGN file')
    } finally {
      setIsUploadingPgn(false)
    }
  }

  const handlePgnTextUpload = async () => {
    if (!pgnText.trim()) {
      toast.error('Please enter PGN content')
      return
    }

    if (!username.trim()) {
      toast.error('Please enter a username first')
      return
    }

    setIsUploadingPgn(true)
    try {
      const formData = new FormData()
      formData.append('username', username.trim())
      formData.append('pgn_text', pgnText.trim())

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/pgn/upload-text`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to upload PGN text')
      }

      const result = await response.json()
      toast.success(`Successfully uploaded ${result.saved_games} games from PGN text!`)
      
      // Clear text area
      setPgnText('')

      // Redirect to games page
      router.push(`/games?username=${username.trim()}`)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to upload PGN text')
    } finally {
      setIsUploadingPgn(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">
          Chess Coach
        </h1>
        <p className="text-xl text-slate-600 mb-8">
          Analyze your Chess.com games with AI-powered insights and improve your play
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
        <h2 className="text-2xl font-semibold text-slate-900 mb-6">
          Get Started
        </h2>
        <div className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-slate-700 mb-2">
              Chess.com Username
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your Chess.com username"
                className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && handleImport()}
              />
            </div>
          </div>
          <button
            onClick={handleImport}
            disabled={isLoading || !username.trim()}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Importing & Analyzing...</span>
              </>
            ) : (
              <>
                <Download size={20} />
                <span>Import & Analyze Games</span>
              </>
            )}
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
        <h2 className="text-2xl font-semibold text-slate-900 mb-6">
          Or Upload PGN Files
        </h2>
        <div className="space-y-6">
          <div>
            <label htmlFor="username-pgn" className="block text-sm font-medium text-slate-700 mb-2">
              Username (for your games)
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
              <input
                id="username-pgn"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Upload PGN File
            </label>
            <div className="flex space-x-4">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pgn"
                onChange={handlePgnFileUpload}
                disabled={isUploadingPgn}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploadingPgn}
                className="flex items-center space-x-2 px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50"
              >
                <Upload size={20} />
                <span>Choose PGN File</span>
              </button>
            </div>
          </div>

          <div>
            <label htmlFor="pgn-text" className="block text-sm font-medium text-slate-700 mb-2">
              Or Paste PGN Text
            </label>
            <textarea
              id="pgn-text"
              value={pgnText}
              onChange={(e) => setPgnText(e.target.value)}
              placeholder="Paste PGN content here..."
              rows={6}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={handlePgnTextUpload}
              disabled={isUploadingPgn || !pgnText.trim()}
              className="mt-2 w-full bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isUploadingPgn ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Uploading PGN...</span>
                </>
              ) : (
                <>
                  <FileText size={20} />
                  <span>Upload PGN Text</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-4">
            <BarChart3 className="text-blue-600 mr-3" size={24} />
            <h3 className="text-lg font-semibold text-slate-900">Game Analysis</h3>
          </div>
          <p className="text-slate-600">
            Get detailed analysis of your games with Stockfish evaluation and mistake detection.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-4">
            <Gamepad2 className="text-green-600 mr-3" size={24} />
            <h3 className="text-lg font-semibold text-slate-900">Personalized Puzzles</h3>
          </div>
          <p className="text-slate-600">
            Practice with puzzles generated from your own mistakes and blunders.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-4">
            <User className="text-purple-600 mr-3" size={24} />
            <h3 className="text-lg font-semibold text-slate-900">AI Coaching</h3>
          </div>
          <p className="text-slate-600">
            Get personalized coaching tips based on your games and GM database patterns.
          </p>
        </div>
      </div>

      <div className="mt-12 text-center">
        <h2 className="text-2xl font-semibold text-slate-900 mb-4">
          How It Works
        </h2>
        <div className="grid md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
              <span className="text-blue-600 font-bold">1</span>
            </div>
            <h3 className="font-medium text-slate-900 mb-2">Import Games</h3>
            <p className="text-sm text-slate-600">Enter your Chess.com username to import your games</p>
          </div>
          <div className="text-center">
            <div className="bg-green-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
              <span className="text-green-600 font-bold">2</span>
            </div>
            <h3 className="font-medium text-slate-900 mb-2">AI Analysis</h3>
            <p className="text-sm text-slate-600">Stockfish analyzes every move with detailed evaluation</p>
          </div>
          <div className="text-center">
            <div className="bg-purple-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
              <span className="text-purple-600 font-bold">3</span>
            </div>
            <h3 className="font-medium text-slate-900 mb-2">Generate Puzzles</h3>
            <p className="text-sm text-slate-600">Create personalized puzzles from your mistakes</p>
          </div>
          <div className="text-center">
            <div className="bg-orange-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
              <span className="text-orange-600 font-bold">4</span>
            </div>
            <h3 className="font-medium text-slate-900 mb-2">Improve</h3>
            <p className="text-sm text-slate-600">Practice and get coaching to improve your game</p>
          </div>
        </div>
      </div>

      {/* Test Chess Board Section */}
      <div className="mt-12 bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center">
          <Square className="mr-2" size={20} />
          Chess Board Test
        </h2>
        <p className="text-slate-600 mb-4">
          This is a test of the chess board component. It should display all 64 squares with proper colors.
        </p>
        <div className="flex justify-center">
          <ChessBoard
            position="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            currentMove={0}
            totalMoves={0}
          />
        </div>
      </div>
    </div>
  )
}

