export type EquityPoint = {
  date: string
  balance: number
  profit?: number
  trade_id?: number
}

export type PerformanceGroup = {
  trades: number
  wins: number
  losses: number
  win_rate: number
  net_profit: number
  average_profit: number
  profit_factor?: number
  breakeven?: number
}

export type SymbolPerformance = {
  trades: number
  wins: number
  losses: number
  profit: number
  gross_profit: number
  gross_loss: number
  average_profit: number
  average_loss: number
  win_rate: number
}

export type StreakStatistics = {
  max_win_streak: number
  max_loss_streak: number
}

export type RStatistics = {
  trades_with_r: number
  average_r: number
  best_r: number
  worst_r: number
  total_r: number
}

export type DrawdownStatistics = {
  max_drawdown: number
  max_drawdown_percent?: number
  current_drawdown?: number
  current_drawdown_percent?: number
}

export type AdvancedAnalytics = {
  total_trades: number
  wins: number
  losses: number
  breakeven: number

  win_rate: number

  net_profit: number
  gross_profit: number
  gross_loss: number

  average_win: number
  average_loss: number

  profit_factor: number

  best_trade: number
  worst_trade: number

  expectancy: number

  streaks: StreakStatistics

  r_multiple: RStatistics

  drawdown: DrawdownStatistics

  equity_curve: EquityPoint[]

  by_symbol: Record<
    string,
    SymbolPerformance
  >

  by_session: Record<
    string,
    PerformanceGroup
  >

  by_strategy: Record<
    string,
    PerformanceGroup
  >

  by_emotion: Record<
    string,
    PerformanceGroup
  >
}
