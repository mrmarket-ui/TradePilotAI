export type StrategyProfile = {
  id: number
  user_id: number

  name: string
  description?: string | null

  markets: string[]
  sessions: string[]
  timeframes: string[]

  entry_rules: string[]
  exit_rules: string[]
  confirmations: string[]

  psychology_rules: string[]
  trade_management_rules: string[]

  max_risk_percent: number
  max_daily_loss_percent: number
  max_weekly_loss_percent: number
  max_trades_per_day: number
  max_consecutive_losses: number

  requires_user_approval: boolean
  is_active: boolean

  created_at: string
  updated_at: string
}


export type StrategyListResponse = {
  total: number
  strategies: StrategyProfile[]
}


export type StrategyCreatePayload = {
  name: string
  description?: string | null

  markets: string[]
  sessions: string[]
  timeframes: string[]

  entry_rules: string[]
  exit_rules: string[]
  confirmations: string[]

  psychology_rules: string[]
  trade_management_rules: string[]

  max_risk_percent: number
  max_daily_loss_percent: number
  max_weekly_loss_percent: number
  max_trades_per_day: number
  max_consecutive_losses: number

  requires_user_approval: boolean
  is_active: boolean
}


export type StrategyUpdatePayload =
  Partial<StrategyCreatePayload>


export type SetupScorePayload = {
  market: string
  session?: string | null
  timeframe?: string | null

  observed_entry_rules: string[]
  observed_confirmations: string[]

  risk_percent: number
  consecutive_losses: number
  trades_today: number

  user_emotion?: string | null
}


export type SetupScoreResponse = {
  strategy_id: number
  strategy_name: string

  overall_score: number
  verdict:
    | "Valid setup"
    | "Watchlist"
    | "Missing confirmation"
    | "Strategy violation"
    | "Excessive risk"
    | "No trade"

  matched_rules: string[]
  missing_rules: string[]

  matched_confirmations: string[]
  missing_confirmations: string[]

  risk_passed: boolean
  psychology_passed: boolean
  daily_limit_passed: boolean

  explanation: string
}


export type StrategyFormState = {
  name: string
  description: string

  markets: string[]
  sessions: string[]
  timeframes: string[]

  entry_rules: string[]
  exit_rules: string[]
  confirmations: string[]

  psychology_rules: string[]
  trade_management_rules: string[]

  max_risk_percent: string
  max_daily_loss_percent: string
  max_weekly_loss_percent: string
  max_trades_per_day: string
  max_consecutive_losses: string

  requires_user_approval: boolean
  is_active: boolean
}


export const emptyStrategyForm: StrategyFormState = {
  name: "",
  description: "",

  markets: [],
  sessions: [],
  timeframes: [],

  entry_rules: [],
  exit_rules: [],
  confirmations: [],

  psychology_rules: [],
  trade_management_rules: [],

  max_risk_percent: "0.5",
  max_daily_loss_percent: "2",
  max_weekly_loss_percent: "5",
  max_trades_per_day: "3",
  max_consecutive_losses: "2",

  requires_user_approval: true,
  is_active: false,
}


export function strategyToForm(
  strategy: StrategyProfile,
): StrategyFormState {
  return {
    name: strategy.name,
    description: strategy.description || "",

    markets: strategy.markets || [],
    sessions: strategy.sessions || [],
    timeframes: strategy.timeframes || [],

    entry_rules: strategy.entry_rules || [],
    exit_rules: strategy.exit_rules || [],
    confirmations:
      strategy.confirmations || [],

    psychology_rules:
      strategy.psychology_rules || [],

    trade_management_rules:
      strategy.trade_management_rules || [],

    max_risk_percent: String(
      strategy.max_risk_percent,
    ),

    max_daily_loss_percent: String(
      strategy.max_daily_loss_percent,
    ),

    max_weekly_loss_percent: String(
      strategy.max_weekly_loss_percent,
    ),

    max_trades_per_day: String(
      strategy.max_trades_per_day,
    ),

    max_consecutive_losses: String(
      strategy.max_consecutive_losses,
    ),

    requires_user_approval:
      strategy.requires_user_approval,

    is_active: strategy.is_active,
  }
}


export function formToStrategyPayload(
  form: StrategyFormState,
): StrategyCreatePayload {
  return {
    name: form.name.trim(),
    description:
      form.description.trim() || null,

    markets: form.markets,
    sessions: form.sessions,
    timeframes: form.timeframes,

    entry_rules: form.entry_rules,
    exit_rules: form.exit_rules,
    confirmations: form.confirmations,

    psychology_rules:
      form.psychology_rules,

    trade_management_rules:
      form.trade_management_rules,

    max_risk_percent: Number(
      form.max_risk_percent,
    ),

    max_daily_loss_percent: Number(
      form.max_daily_loss_percent,
    ),

    max_weekly_loss_percent: Number(
      form.max_weekly_loss_percent,
    ),

    max_trades_per_day: Number(
      form.max_trades_per_day,
    ),

    max_consecutive_losses: Number(
      form.max_consecutive_losses,
    ),

    requires_user_approval:
      form.requires_user_approval,

    is_active: form.is_active,
  }
}
