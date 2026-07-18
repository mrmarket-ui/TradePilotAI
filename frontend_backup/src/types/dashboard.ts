export type DashboardPayload = {
  intelligence?: { headline?: { title?: string; message?: string }; mission?: { today?: string; this_week?: string }; scorecard?: { overall?: number; risk?: number; psychology?: number; discipline?: number; consistency?: number } }
  summary?: { total_trades?: number; wins?: number; losses?: number; breakeven?: number; win_rate?: number; net_profit?: number; gross_profit?: number; gross_loss?: number; average_win?: number; average_loss?: number; profit_factor?: number; best_trade?: number; worst_trade?: number }
  equity_curve?: Array<{ date: string; balance: number }>
  monthly_profit?: Record<string, number>
  symbols?: Array<{ pair: string; count: number }>
  recent_trades?: Array<{ id: number; pair: string; direction: string; profit: number; lot_size?: number | null; strategy?: string | null; opened_at?: string | null; closed_at?: string | null }>
}
