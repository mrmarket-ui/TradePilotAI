import api from "@/api/client"

import type {
  SetupScorePayload,
  SetupScoreResponse,
  StrategyCreatePayload,
  StrategyListResponse,
  StrategyProfile,
  StrategyUpdatePayload,
} from "@/types/strategy"


export async function fetchStrategies(): Promise<StrategyListResponse> {
  const response = await api.get<StrategyListResponse>(
    "/strategies",
  )

  return response.data
}


export async function fetchStrategy(
  strategyId: number,
): Promise<StrategyProfile> {
  const response = await api.get<StrategyProfile>(
    `/strategies/${strategyId}`,
  )

  return response.data
}


export async function createStrategy(
  payload: StrategyCreatePayload,
): Promise<StrategyProfile> {
  const response = await api.post<StrategyProfile>(
    "/strategies",
    payload,
  )

  return response.data
}


export async function updateStrategy(
  strategyId: number,
  payload: StrategyUpdatePayload,
): Promise<StrategyProfile> {
  const response = await api.patch<StrategyProfile>(
    `/strategies/${strategyId}`,
    payload,
  )

  return response.data
}


export async function deleteStrategy(
  strategyId: number,
): Promise<void> {
  await api.delete(
    `/strategies/${strategyId}`,
  )
}


export async function activateStrategy(
  strategyId: number,
): Promise<StrategyProfile> {
  const response = await api.post<StrategyProfile>(
    `/strategies/${strategyId}/activate`,
  )

  return response.data
}


export async function scoreStrategySetup(
  strategyId: number,
  payload: SetupScorePayload,
): Promise<SetupScoreResponse> {
  const response = await api.post<SetupScoreResponse>(
    `/strategies/${strategyId}/score`,
    payload,
  )

  return response.data
}
