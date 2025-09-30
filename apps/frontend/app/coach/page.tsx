'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { MessageCircle, Bot, User, Send, Lightbulb, Target, TrendingUp } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface CoachMessage {
  id: string
  type: 'user' | 'coach'
  content: string
  timestamp: Date
  analysis?: {
    eval_swing: number
    best_move: string
    explanation: string
  }
  human_examples?: Array<{
    game_id: string
    players: string
    move: string
    explanation: string
  }>
}

export default function CoachPage() {
  const searchParams = useSearchParams()
  const username = searchParams.get('username') || ''
  
  const [messages, setMessages] = useState<CoachMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    if (username) {
      fetchStats()
      // Add welcome message
      setMessages([{
        id: '1',
        type: 'coach',
        content: `Hello ${username}! I'm your chess coach. I can help you analyze your games, explain mistakes, and suggest improvements. What would you like to know?`,
        timestamp: new Date()
      }])
    }
  }, [username])

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

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: CoachMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Simulate coach response (in real implementation, this would call the API)
      const coachResponse = await generateCoachResponse(inputMessage, stats)
      
      const coachMessage: CoachMessage = {
        id: (Date.now() + 1).toString(),
        type: 'coach',
        content: coachResponse.content,
        timestamp: new Date(),
        analysis: coachResponse.analysis,
        human_examples: coachResponse.human_examples
      }

      setMessages(prev => [...prev, coachMessage])
    } catch (error) {
      toast.error('Failed to get coach response')
    } finally {
      setIsLoading(false)
    }
  }

  const generateCoachResponse = async (message: string, stats: any): Promise<any> => {
    // This is a mock implementation - in reality, this would call your AI service
    const lowerMessage = message.toLowerCase()
    
    if (lowerMessage.includes('blunder') || lowerMessage.includes('mistake')) {
      return {
        content: `Based on your recent games, you have a ${stats?.blunder_rate?.toFixed(1) || 0}% blunder rate. Here are some tips to reduce blunders:

1. **Double-check captures**: Before taking a piece, make sure it's not defended
2. **Look for checks**: Always check if your move allows the opponent to give check
3. **Calculate variations**: Spend a few extra seconds calculating the opponent's best response
4. **Avoid time pressure**: Don't rush moves in critical positions`,
        analysis: {
          eval_swing: -250,
          best_move: 'Qd1',
          explanation: 'The queen should retreat to safety instead of being captured'
        },
        human_examples: [{
          game_id: 'example1',
          players: 'Carlsen vs Nakamura',
          move: 'Qd1',
          explanation: 'In this similar position, Carlsen retreated the queen to safety'
        }]
      }
    }
    
    if (lowerMessage.includes('opening') || lowerMessage.includes('start')) {
      return {
        content: `Your opening choices show good variety! Here's what I noticed:

**Most Played Openings:**
- Sicilian Defense (25% of games)
- Queen's Gambit (20% of games)
- King's Indian Defense (15% of games)

**Recommendations:**
1. **Study your main lines deeper** - Focus on 2-3 openings and learn them well
2. **Learn typical middlegame plans** - Don't just memorize moves
3. **Practice against different setups** - Be prepared for various responses`,
        human_examples: [{
          game_id: 'example2',
          players: 'Kasparov vs Karpov',
          move: 'Nf3',
          explanation: 'This is a typical development move in the Queen\'s Gambit'
        }]
      }
    }
    
    if (lowerMessage.includes('improve') || lowerMessage.includes('better')) {
      return {
        content: `Here's your improvement roadmap based on your games:

**Priority 1: Reduce Blunders** (${stats?.blunder_rate?.toFixed(1) || 0}% current rate)
- Practice calculation exercises
- Take more time in critical positions
- Double-check before moving

**Priority 2: Improve Tactical Vision**
- Solve 10 puzzles daily
- Focus on patterns you miss most often
- Practice with time pressure

**Priority 3: Endgame Study**
- Learn basic king and pawn endgames
- Practice with fewer pieces on the board
- Study theoretical positions`,
        analysis: {
          eval_swing: 0,
          best_move: 'Study',
          explanation: 'Consistent study and practice will improve your overall game'
        }
      }
    }
    
    return {
      content: `I understand you're asking about "${message}". Let me analyze your games to give you specific advice. 

Based on your recent performance, I can see areas where you can improve. Would you like me to focus on:
- Reducing blunders and mistakes
- Improving your opening repertoire  
- Enhancing tactical vision
- Better endgame play

What specific aspect of your game would you like to work on?`,
      human_examples: []
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">
          Chess Coach
        </h1>
        <p className="text-slate-600">
          Get personalized coaching based on your games
        </p>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow h-96 flex flex-col">
            <div className="p-4 border-b border-slate-200">
              <div className="flex items-center space-x-2">
                <MessageCircle className="text-blue-600" size={20} />
                <h2 className="text-lg font-semibold text-slate-900">Chat with Coach</h2>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-900'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      {message.type === 'coach' && (
                        <Bot className="text-blue-600 mt-1" size={16} />
                      )}
                      {message.type === 'user' && (
                        <User className="text-white mt-1" size={16} />
                      )}
                      <div className="flex-1">
                        <p className="text-sm">{message.content}</p>
                        
                        {message.analysis && (
                          <div className="mt-2 p-2 bg-white bg-opacity-20 rounded text-xs">
                            <div className="font-medium">Analysis:</div>
                            <div>Eval swing: {message.analysis.eval_swing > 0 ? '+' : ''}{message.analysis.eval_swing}</div>
                            <div>Best move: {message.analysis.best_move}</div>
                            <div>{message.analysis.explanation}</div>
                          </div>
                        )}
                        
                        {message.human_examples && message.human_examples.length > 0 && (
                          <div className="mt-2 p-2 bg-white bg-opacity-20 rounded text-xs">
                            <div className="font-medium">GM Examples:</div>
                            {message.human_examples.map((example, idx) => (
                              <div key={idx} className="mt-1">
                                <div className="font-medium">{example.players}</div>
                                <div>Move: {example.move}</div>
                                <div>{example.explanation}</div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-100 text-slate-900 px-4 py-2 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <Bot className="text-blue-600" size={16} />
                      <div className="animate-pulse">Coach is thinking...</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <div className="p-4 border-t border-slate-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask your coach anything..."
                  className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isLoading}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Quick Tips</h2>
            <div className="space-y-3">
              <button
                onClick={() => setInputMessage('How can I reduce blunders?')}
                className="w-full text-left p-3 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <Target className="text-red-600" size={16} />
                  <span className="text-sm font-medium text-red-800">Reduce Blunders</span>
                </div>
              </button>
              
              <button
                onClick={() => setInputMessage('What should I study in openings?')}
                className="w-full text-left p-3 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <Lightbulb className="text-blue-600" size={16} />
                  <span className="text-sm font-medium text-blue-800">Opening Study</span>
                </div>
              </button>
              
              <button
                onClick={() => setInputMessage('How can I improve my game?')}
                className="w-full text-left p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <TrendingUp className="text-green-600" size={16} />
                  <span className="text-sm font-medium text-green-800">Improve Overall</span>
                </div>
              </button>
            </div>
          </div>

          {stats && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Your Stats</h2>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Total Games:</span>
                  <span className="font-medium">{stats.total_games}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Blunder Rate:</span>
                  <span className="font-medium text-red-600">{stats.blunder_rate?.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Mistake Rate:</span>
                  <span className="font-medium text-orange-600">{stats.mistake_rate?.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Inaccuracy Rate:</span>
                  <span className="font-medium text-yellow-600">{stats.inaccuracy_rate?.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

