import api from "@/api/client"
import type {
  Trade,
  TradeListResponse,
  TradePayload,
  TradeReview,
} from "@/types/trade"

export async function fetchTrades(): Promise<TradeListResponse> {
  const response = await api.get<TradeListResponse>("/trades", {
    params: { skip: 0, limit: 200 },
  })
  return response.data
}

export async function createTrade(payload: TradePayload): Promise<Trade> {
  const response = await api.post<Trade>("/trades", payload)
  return response.data
}

export async function updateTrade(
  tradeId: number,
  payload: Partial<TradePayload>,
): Promise<Trade> {
  const response = await api.patch<Trade>(`/trades/${tradeId}`, payload)
  return response.data
}

export async function deleteTrade(tradeId: number): Promise<void> {
  await api.delete(`/trades/${tradeId}`)
}

export async function fetchTradeReview(tradeId: number): Promise<TradeReview> {
  const response = await api.get<TradeReview>(`/trades/${tradeId}/review`)
  return response.data
}
