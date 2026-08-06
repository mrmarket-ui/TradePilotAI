import {api} from "@/api"


export type StrategyProfile = {
  id: number
  name: string
  description?: string | null
  strategy_type?: string

  markets: string[]
  allowed_symbols: string[]
  blocked_symbols: string[]

  preferred_direction?: string

  sessions: string[]
  timeframes: string[]

  entry_rules: string[]
  exit_rules: string[]
  confirmations: string[]

  psychology_rules: string[]
  trade_management_rules: string[]

  max_risk_percent: number
  min_risk_reward: number

  max_daily_loss_percent: number
  max_weekly_loss_percent: number

  max_trades_per_day: number
  max_consecutive_losses: number

  requires_user_approval: boolean

  is_active: boolean
  is_archived: boolean
}


export type StrategyListResponse = {
  total: number
  strategies: StrategyProfile[]
}


export async function getSavedStrategies():
Promise<StrategyListResponse> {
  const response =
    await api.get<StrategyListResponse>(
      "/strategies",
    )

  return response.data
}
