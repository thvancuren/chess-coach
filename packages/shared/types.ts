// Shared TypeScript types for Chess Coach

export interface Game {
  id: string
  username: string
  site: string
  eco?: string
  opening?: string
  result?: string
  time_control?: string
  white?: string
  black?: string
  started_at?: string
  created_at: string
}

export interface Move {
  id: string
  ply: number
  fen: string
  san: string
  side: 'white' | 'black'
  time_left_ms?: number
  sf_eval_cp?: number
  sf_mate?: number
  sf_bestmove_uci?: string
  sf_pv?: string
  mistake_tag: 'none' | 'inacc' | 'mistake' | 'blunder'
}

export interface GameDetail extends Game {
  pgn: string
  moves: Move[]
  features?: {
    counts_by_motif?: Record<string, number>
    blunder_rate_by_phase?: Record<string, number>
    time_profile?: Record<string, any>
  }
}

export interface Puzzle {
  id: string
  fen_start: string
  solution_san: string[]
  motif?: string
  strength: number
  created_at: string
}

export interface HumanNeighbor {
  ref_game_id: string
  ref_ply: number
  similarity: number
  human_choice_san: string
  meta?: Record<string, any>
}

export interface AnalysisStatus {
  username: string
  job_type: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  total_items?: number
  processed_items: number
  error_message?: string
  created_at: string
  completed_at?: string
}

export interface StatsSummary {
  username: string
  total_games: number
  blunder_rate: number
  mistake_rate: number
  inaccuracy_rate: number
  blunder_rate_by_phase: Record<string, number>
  common_motifs: Array<{
    motif: string
    count: number
  }>
  time_profile?: Record<string, any>
}

export interface SparringSession {
  session_id: string
  username: string
  difficulty: number
  style_hints?: Record<string, any>
  created_at: string
}

// API Request/Response types
export interface ChessComImportRequest {
  username: string
  from_date?: string
  to_date?: string
}

export interface BatchAnalysisRequest {
  username: string
  max_depth?: number
}

export interface SparringSessionRequest {
  username: string
  difficulty: number
  style_hints?: Record<string, any>
}

// WebSocket message types
export interface AnalysisProgressMessage {
  username: string
  job_type: string
  status: string
  progress: number
  total_items?: number
  processed_items: number
  message?: string
}

// UI Component props
export interface ChessBoardProps {
  position: string
  onMoveClick?: (moveIndex: number) => void
  currentMove?: number
  totalMoves?: number
}

export interface EvalGraphProps {
  data: Array<{
    move: number
    eval: number
    mate?: number | null
    mistake: string
  }>
  currentMove?: number
}

export interface PuzzleCardProps {
  puzzle: Puzzle
  onSolve?: (puzzleId: string) => void
  onNext?: () => void
}

export interface CoachMessageProps {
  message: {
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
}

