export type Trade = {
  id: number
  user_id: number
  broker?: string | null
  ticket?: string | null
  pair: string
  direction: "BUY" | "SELL"
  entry: number
  exit_price?: number | null
  stop_loss: number
  take_profit: number
  lot_size?: number | null
  profit?: number | null
  commission?: number
  swap?: number
  strategy?: string | null
  emotion?: string | null
  notes?: string | null
  opened_at?: string | null
  closed_at?: string | null
  created_at: string
  imported?: boolean
}

export type TradeListResponse = { total: number; trades: Trade[] }

export type TradePayload = {
  broker?: string | null
  ticket?: string | null
  pair: string
  direction: "BUY" | "SELL"
  entry: number
  exit_price?: number | null
  stop_loss: number
  take_profit: number
  lot_size?: number | null
  profit?: number | null
  commission?: number
  swap?: number
  strategy?: string | null
  emotion?: string | null
  notes?: string | null
  opened_at?: string | null
  closed_at?: string | null
  imported?: boolean
}

export type TradeReview = {
  trade_score: number
  summary: string
  strengths: string[]
  mistakes: string[]
  lesson: string
  next_mission: string
}
