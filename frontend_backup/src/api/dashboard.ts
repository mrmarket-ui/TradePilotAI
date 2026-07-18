import api from "@/api/client"
import type { DashboardPayload } from "@/types/dashboard"
export async function fetchDashboard(): Promise<DashboardPayload> {
  return (await api.get<DashboardPayload>("/analytics/dashboard")).data
}
