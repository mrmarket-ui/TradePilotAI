import api from "@/api/client"
import type { Trade, TradeListResponse, TradePayload, TradeReview } from "@/types/trade"

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

export async function updateTrade(id: number, payload: Partial<TradePayload>): Promise<Trade> {
  const response = await api.patch<Trade>(`/trades/${id}`, payload)
  return response.data
}

export async function deleteTrade(id: number): Promise<void> {
  await api.delete(`/trades/${id}`)
}

export async function fetchTradeReview(id: number): Promise<TradeReview> {
  const response = await api.get<TradeReview>(`/trades/${id}/review`)
  return response.data
}
