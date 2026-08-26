export type TradingCalendarDay = {
  date: string
  trades: number
  wins: number
  losses: number
  breakeven: number
  net_profit: number
  win_rate: number
  result:
    | "profit"
    | "loss"
    | "breakeven"
}

export type TradingCalendarResponse = {
  total_days: number
  days: TradingCalendarDay[]
}
