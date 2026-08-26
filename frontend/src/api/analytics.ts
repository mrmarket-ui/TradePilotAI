import api from "@/api/client"

import type {
  AdvancedAnalytics,
} from "@/types/analytics"


export async function fetchAdvancedAnalytics():
Promise<AdvancedAnalytics> {

  const response =
    await api.get<AdvancedAnalytics>(
      "/trading/analytics",
    )

  return response.data
}
