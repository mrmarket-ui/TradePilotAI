import { api } from "@/api"
import type { PartnerOffer } from "@/api/partnerExtras"

export type AdminPartnerOffer = PartnerOffer & {
  active: boolean
}

export const getAdminPartnerOffers = async () =>
  (
    await api.get<{
      total: number
      offers: AdminPartnerOffer[]
    }>("/admin/partner-offers")
  ).data

export const createAdminPartnerOffer = async (
  payload: {
    partner_id: number
    title: string
    description?: string
    coupon_code?: string
    offer_url?: string
    active?: boolean
    expires_at?: string | null
  },
) =>
  (
    await api.post(
      "/admin/partner-offers",
      payload,
    )
  ).data

export const updateAdminPartnerOffer = async (
  offerId: number,
  payload: Partial<AdminPartnerOffer>,
) =>
  (
    await api.patch(
      `/admin/partner-offers/${offerId}`,
      payload,
    )
  ).data

export const disableAdminPartnerOffer = async (
  offerId: number,
) =>
  (
    await api.delete(
      `/admin/partner-offers/${offerId}`,
    )
  ).data
