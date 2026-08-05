import { api } from "@/api"

export type Partner = {
  id: number
  name: string
  slug: string
  category: "broker" | "prop_firm"
  description?: string | null
  referral_url: string
  badge?: string | null
  logo_url?: string | null
  status: string
  featured: boolean
  display_order: number
  minimum_deposit?: string | null
  platforms?: string[] | null
  demo_available?: boolean | null
  regulation?: string | null
  challenge_size?: string | null
  challenge_fee?: string | null
  profit_split?: string | null
  max_drawdown?: string | null
  payout_frequency?: string | null
  created_at: string
  updated_at: string
}

export const getPartners = async (
  category?: string,
  search?: string,
) =>
  (
    await api.get<Partner[]>(
      "/partners",
      {
        params: {
          ...(category ? { category } : {}),
          ...(search ? { search } : {}),
        },
      },
    )
  ).data

export const getSavedPartners = async () =>
  (
    await api.get<Partner[]>(
      "/partners/saved",
    )
  ).data

export const trackPartnerClick = async (
  partnerId: number,
  source = "partners_page",
) =>
  (
    await api.post(
      `/partners/${partnerId}/click`,
      { source },
    )
  ).data

export const savePartner = async (
  partnerId: number,
) =>
  (
    await api.post(
      `/partners/${partnerId}/save`,
    )
  ).data

export const unsavePartner = async (
  partnerId: number,
) =>
  (
    await api.delete(
      `/partners/${partnerId}/save`,
    )
  ).data
