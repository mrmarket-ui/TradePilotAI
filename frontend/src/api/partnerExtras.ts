import { api } from "@/api"

export type PartnerReview = {
  id: number
  rating: number
  review?: string | null
  created_at: string
  user: string
}

export type PartnerReviewsResponse = {
  average_rating: number
  review_count: number
  reviews: PartnerReview[]
}

export type PartnerOffer = {
  id: number
  partner_id: number
  title: string
  description?: string | null
  coupon_code?: string | null
  offer_url?: string | null
  expires_at?: string | null
}

export const getPartnerReviews = async (
  partnerId: number,
) =>
  (
    await api.get<PartnerReviewsResponse>(
      `/partners/${partnerId}/reviews`,
    )
  ).data

export const submitPartnerReview = async (
  partnerId: number,
  rating: number,
  review: string,
) =>
  (
    await api.post(
      `/partners/${partnerId}/reviews`,
      {
        rating,
        review,
      },
    )
  ).data

export const getPartnerOffers = async (
  partnerId: number,
) =>
  (
    await api.get<PartnerOffer[]>(
      `/partners/${partnerId}/offers`,
    )
  ).data
