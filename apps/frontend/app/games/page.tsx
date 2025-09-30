'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Gamepad2, Calendar, Clock, Trophy, AlertTriangle } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface Game {
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
}

export default function GamesPage() {
  const searchParams = useSearchParams()
  const username = searchParams.get('username') || ''
  
  const [games, setGames] = useState<Game[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    if (username) {
      fetchGames()
      fetchStats()
    }
  }, [username])

  const fetchGames = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/games?username=${username}&limit=50`
      )
      if (response.ok) {
        const data = await response.json()
        setGames(data)
      }
    } catch (error) {
      toast.error('Failed to fetch games')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/games/stats/summary?username=${username}`
      )
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const getResultIcon = (result: string | null) => {
    switch (result) {
      case '1-0':
        return <Trophy className="text-green-600" size={16} />
      case '0-1':
        return <Trophy className="text-red-600" size={16} />
      case '1/2-1/2':
        return <Trophy className="text-yellow-600" size={16} />
      default:
        return null
    }
  }

  const getResultText = (result: string | null) => {
    switch (result) {
      case '1-0':
        return 'White Wins'
      case '0-1':
        return 'Black Wins'
      case '1/2-1/2':
        return 'Draw'
      default:
        return 'Unknown'
    }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown'
    return new Date(dateString).toLocaleDateString()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">
          Games for {username}
        </h1>
        <p className="text-slate-600">
          {games.length} games found
        </p>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Gamepad2 className="text-blue-600 mr-3" size={24} />
              <div>
                <p className="text-sm text-slate-600">Total Games</p>
                <p className="text-2xl font-bold text-slate-900">{stats.total_games}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <AlertTriangle className="text-red-600 mr-3" size={24} />
              <div>
                <p className="text-sm text-slate-600">Blunder Rate</p>
                <p className="text-2xl font-bold text-slate-900">{stats.blunder_rate.toFixed(1)}%</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <AlertTriangle className="text-orange-600 mr-3" size={24} />
              <div>
                <p className="text-sm text-slate-600">Mistake Rate</p>
                <p className="text-2xl font-bold text-slate-900">{stats.mistake_rate.toFixed(1)}%</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <AlertTriangle className="text-yellow-600 mr-3" size={24} />
              <div>
                <p className="text-sm text-slate-600">Inaccuracy Rate</p>
                <p className="text-2xl font-bold text-slate-900">{stats.inaccuracy_rate.toFixed(1)}%</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">Recent Games</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Players
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Opening
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Time Control
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Result
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {games.map((game) => (
                <tr key={game.id} className="hover:bg-slate-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                    <div className="flex items-center">
                      <Calendar className="mr-2 text-slate-400" size={16} />
                      {formatDate(game.started_at)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                    <div>
                      <div className="font-medium">{game.white}</div>
                      <div className="text-slate-500">vs</div>
                      <div className="font-medium">{game.black}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                    <div>
                      <div className="font-medium">{game.eco || 'N/A'}</div>
                      <div className="text-slate-500 text-xs">{game.opening || 'Unknown'}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                    <div className="flex items-center">
                      <Clock className="mr-2 text-slate-400" size={16} />
                      {game.time_control || 'N/A'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                    <div className="flex items-center">
                      {getResultIcon(game.result)}
                      <span className="ml-2">{getResultText(game.result)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <Link
                      href={`/game/${game.id}`}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      View Game
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {games.length === 0 && (
        <div className="text-center py-12">
          <Gamepad2 className="mx-auto text-slate-400 mb-4" size={48} />
          <h3 className="text-lg font-medium text-slate-900 mb-2">No games found</h3>
          <p className="text-slate-600 mb-4">
            Import some games to get started with analysis
          </p>
          <Link
            href="/"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Import Games
          </Link>
        </div>
      )}
    </div>
  )
}

