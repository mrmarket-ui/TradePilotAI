import {api} from "@/api"


export type AISignal = {
  id: number

  strategy_id?: number | null

  symbol: string
  timeframe?: string | null

  direction:
    | "BUY"
    | "SELL"
    | "NO_TRADE"

  confidence: number
  setup_score: number

  entry_low?: number | null
  entry_high?: number | null

  stop_loss?: number | null

  take_profit_1?: number | null
  take_profit_2?: number | null
  take_profit_3?: number | null

  risk_reward?: number | null

  matched_rules: string[]
  missing_rules: string[]

  reasoning?: string | null
  invalidation?: string | null

  status: string
  user_approved: boolean

  created_at: string
}


export type AISignalHistoryResponse = {
  total: number
  signals: AISignal[]
}


export type PaperTrade = {
  id: number
  user_id: number
  signal_id: number

  symbol: string

  direction:
    | "BUY"
    | "SELL"

  entry_price: number

  stop_loss?: number | null
  take_profit?: number | null

  risk_percent: number

  status: string

  exit_price?: number | null
  profit_loss?: number | null

  opened_at: string
  closed_at?: string | null
}


export type PaperTradeHistoryResponse = {
  total: number
  trades: PaperTrade[]
}


export async function analyzeChart(
  payload: {
    strategyId: number
    symbol: string
    timeframe: string
    chart: File
  },
): Promise<AISignal> {
  const form =
    new FormData()

  form.append(
    "strategy_id",
    String(
      payload.strategyId,
    ),
  )

  form.append(
    "symbol",
    payload.symbol
      .trim()
      .toUpperCase(),
  )

  form.append(
    "timeframe",
    payload.timeframe.trim(),
  )

  form.append(
    "chart",
    payload.chart,
  )

  const response =
    await api.post<AISignal>(
      "/ai-signals/analyze-chart",
      form,
      {
        headers: {
          "Content-Type":
            "multipart/form-data",
        },
      },
    )

  return response.data
}


export async function getAISignals():
Promise<AISignalHistoryResponse> {
  const response =
    await api.get<AISignalHistoryResponse>(
      "/ai-signals",
    )

  return response.data
}


export async function approveAISignal(
  id: number,
  approved: boolean,
) {
  const response =
    await api.patch(
      `/ai-signals/${id}/approval`,
      {
        approved,
      },
    )

  return response.data
}


export async function paperTradeSignal(
  signalId: number,
  entryPrice: number,
  riskPercent: number,
): Promise<PaperTrade> {
  const response =
    await api.post<PaperTrade>(
      "/ai-signals/paper-trades",
      {
        signal_id:
          signalId,

        entry_price:
          entryPrice,

        risk_percent:
          riskPercent,
      },
    )

  return response.data
}


export async function getPaperTrades():
Promise<PaperTradeHistoryResponse> {
  const response =
    await api.get<PaperTradeHistoryResponse>(
      "/ai-signals/paper-trades",
    )

  return response.data
}


export async function closePaperTrade(
  tradeId: number,
  exitPrice: number,
): Promise<PaperTrade> {
  const response =
    await api.patch<PaperTrade>(
      `/ai-signals/paper-trades/${tradeId}/close`,
      {
        exit_price:
          exitPrice,
      },
    )

  return response.data
}
