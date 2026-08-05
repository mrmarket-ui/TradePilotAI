import { api } from "@/api"
import type { Partner } from "@/api/partners"

export type AdminPartnerAnalytics = {
  total_clicks: number
  total_partners: number
  active_partners: number
  saved_count: number
  partners: {
    partner_id: number
    name: string
    category: string
    clicks: number
  }[]
  sources: {
    source: string
    clicks: number
  }[]
}

export const getAdminPartners = async () =>
  (
    await api.get<{
      total: number
      partners: Partner[]
    }>("/admin/partners")
  ).data

export const getAdminPartnerAnalytics = async (
  days = 30,
) =>
  (
    await api.get<AdminPartnerAnalytics>(
      "/admin/partners/analytics/overview",
      {
        params: { days },
      },
    )
  ).data

export const createAdminPartner = async (
  payload: Partial<Partner>,
) =>
  (
    await api.post<Partner>(
      "/admin/partners",
      payload,
    )
  ).data

export const updateAdminPartner = async (
  partnerId: number,
  payload: Partial<Partner>,
) =>
  (
    await api.patch<Partner>(
      `/admin/partners/${partnerId}`,
      payload,
    )
  ).data

export const updateAdminPartnerStatus = async (
  partnerId: number,
  status: string,
) =>
  (
    await api.patch(
      `/admin/partners/${partnerId}/status`,
      null,
      {
        params: { status },
      },
    )
  ).data


