import api from "@/api/client"

import type {
  TradingCalendarResponse,
} from "@/types/calendar"


export async function fetchTradingCalendar():
Promise<TradingCalendarResponse> {

  const response =
    await api.get<TradingCalendarResponse>(
      "/trading/calendar",
    )

  return response.data
}
