import { api } from "@/api"

export type AdminOverview = {
  admin: {
    id: number
    email: string
  }
  users: {
    total: number
    active: number
    pro: number
    premium: number
  }
  subscriptions: {
    active: number
    pending: number
  }
  trades: {
    total: number
  }
  system: {
    status: string
  }
}

export type AdminUser = {
  id: number
  email: string
  full_name?: string | null
  username?: string | null
  plan: string
  is_active: boolean
  is_admin: boolean
  ai_credits: number
  created_at: string
}

export type AdminUsersResponse = {
  total: number
  limit: number
  offset: number
  users: AdminUser[]
}

export type AdminSubscription = {
  id: number
  user_id: number
  provider: string
  plan: string
  status: string
  paypal_subscription_id?: string | null
  payer_email?: string | null
  currency: string
  amount?: string | null
  next_billing_at?: string | null
  last_payment_at?: string | null
  created_at: string
  updated_at: string
}

export type AdminSubscriptionsResponse = {
  total: number
  limit: number
  offset: number
  subscriptions: AdminSubscription[]
}

export type AdminHealth = {
  api: string
  database: string
}

export type AdminWebhookEvent = {
  id: number
  paypal_event_id: string
  event_type: string
  resource_id?: string | null
  processing_status: string
  error_message?: string | null
  received_at: string
  processed_at?: string | null
}

export const getAdminOverview = async () =>
  (await api.get<AdminOverview>("/admin/overview")).data

export const getAdminUsers = async (
  search = "",
) =>
  (
    await api.get<AdminUsersResponse>(
      "/admin/users",
      {
        params: search
          ? { search }
          : undefined,
      },
    )
  ).data

export const changeAdminUserPlan = async (
  userId: number,
  plan: "free" | "pro" | "premium",
) =>
  (
    await api.patch(
      `/admin/users/${userId}/plan`,
      null,
      {
        params: { plan },
      },
    )
  ).data

export const changeAdminUserStatus = async (
  userId: number,
  isActive: boolean,
) =>
  (
    await api.patch(
      `/admin/users/${userId}/status`,
      null,
      {
        params: {
          is_active: isActive,
        },
      },
    )
  ).data

export const changeAdminUserCredits = async (
  userId: number,
  credits: number,
) =>
  (
    await api.patch(
      `/admin/users/${userId}/ai-credits`,
      null,
      {
        params: { credits },
      },
    )
  ).data

export const getAdminSubscriptions = async () =>
  (
    await api.get<AdminSubscriptionsResponse>(
      "/admin/subscriptions",
    )
  ).data

export const getAdminHealth = async () =>
  (
    await api.get<AdminHealth>(
      "/admin/system/health",
    )
  ).data

export const getAdminWebhooks = async () =>
  (
    await api.get<{
      total: number
      events: AdminWebhookEvent[]
    }>(
      "/admin/system/webhooks",
    )
  ).data
