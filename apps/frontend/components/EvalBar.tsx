'use client'

interface EvalBarProps {
  evaluation: number | null
  mate: number | null
  isWhiteToMove: boolean
  whitePlayer?: string
  blackPlayer?: string
}

export default function EvalBar({ evaluation, mate, isWhiteToMove, whitePlayer, blackPlayer }: EvalBarProps) {
  // Convert centipawns to a percentage (0-100)
  const getWinPercentage = (cp: number | null, mate: number | null, isWhiteToMove: boolean) => {
    if (mate !== null) {
      // If there's a mate, return 100% for the winning side
      const mateForWhite = mate > 0
      return mateForWhite ? 100 : 0
    }
    
    if (cp === null) return 50 // Equal position
    
    // Convert centipawns to win percentage using sigmoid function
    // This gives a more realistic win probability curve
    const sigmoid = (x: number) => 1 / (1 + Math.exp(-x / 200))
    const rawPercentage = sigmoid(cp) * 100
    
    // Ensure we don't go below 1% or above 99% for non-mate positions
    return Math.max(1, Math.min(99, rawPercentage))
  }

  const winPercentage = getWinPercentage(evaluation, mate, isWhiteToMove)
  const isMate = mate !== null && Math.abs(mate) <= 10
  const mateForWhite = mate !== null && mate > 0

  // Determine colors and content
  let leftColor = 'bg-slate-200'
  let rightColor = 'bg-slate-200'
  let leftText = whitePlayer || 'White'
  let rightText = blackPlayer || 'Black'
  let centerText = ''

  if (isMate) {
    if (mateForWhite) {
      leftColor = 'bg-white'
      rightColor = 'bg-slate-600'
      centerText = `M${mate}`
    } else {
      leftColor = 'bg-slate-600'
      rightColor = 'bg-white'
      centerText = `M${Math.abs(mate)}`
    }
  } else {
    // Use gradient based on win percentage
    if (winPercentage > 50) {
      // White advantage
      leftColor = 'bg-white'
      rightColor = 'bg-slate-300'
    } else {
      // Black advantage
      leftColor = 'bg-slate-300'
      rightColor = 'bg-slate-800'
      rightText = blackPlayer || 'Black'
    }
  }

  return (
    <div className="w-full bg-slate-100 rounded-lg p-2">
      <div className="flex items-center justify-between text-sm font-medium text-slate-700 mb-1">
        <span>{leftText}</span>
        <span>{rightText}</span>
      </div>
      
      <div className="relative h-8 bg-slate-200 rounded-lg overflow-hidden">
        {/* Left side (White) */}
        <div 
          className={`absolute left-0 top-0 h-full ${leftColor} transition-all duration-300 ease-out`}
          style={{ width: `${winPercentage}%` }}
        />
        
        {/* Right side (Black) */}
        <div 
          className={`absolute right-0 top-0 h-full ${rightColor} transition-all duration-300 ease-out`}
          style={{ width: `${100 - winPercentage}%` }}
        />
        
        {/* Center text for mate */}
        {isMate && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="font-bold text-lg text-slate-800 drop-shadow-sm">
              {centerText}
            </span>
          </div>
        )}
        
        {/* Evaluation text for non-mate positions */}
        {!isMate && evaluation !== null && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="font-medium text-sm text-slate-700 bg-white/80 px-2 py-1 rounded shadow-sm">
              {evaluation > 0 ? '+' : ''}{(evaluation / 100).toFixed(1)}
            </span>
          </div>
        )}
      </div>
      
      {/* Win percentage display */}
      {!isMate && (
        <div className="flex justify-between text-xs text-slate-500 mt-1">
          <span>{winPercentage.toFixed(1)}%</span>
          <span>{(100 - winPercentage).toFixed(1)}%</span>
        </div>
      )}
    </div>
  )
}
