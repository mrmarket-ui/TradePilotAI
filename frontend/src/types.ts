export type AuthUser = {
  id?: number
  email: string
  full_name?: string | null
  username?: string | null
  avatar?: string | null
  bio?: string | null
  plan?: "free" | "pro" | "premium"
  is_active?: boolean
  is_admin?: boolean
  ai_credits?: number
  preferred_language?: string
  preferred_currency?: string
  created_at?: string
}

export type LoginCredentials = {
  email: string
  password: string
}

export type LoginResponse = {
  access_token?: string
  token?: string
  token_type?: string
  user?: AuthUser
}

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
}

export type TradeListResponse = {
  total: number
  trades: Trade[]
}

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
