import api from "@/api/client"

import type {
  SetupScorePayload,
  SetupScoreResponse,
} from "@/types/setupScore"

export async function scoreSetup(
  strategyId: number,
  payload: SetupScorePayload,
): Promise<SetupScoreResponse> {
  const response =
    await api.post<SetupScoreResponse>(
      `/strategies/${strategyId}/score`,
      payload,
    )

  return response.data
}
