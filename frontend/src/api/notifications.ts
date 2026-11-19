import api from "@/api/client"

export type AppNotification = {
  id: number
  type: string
  severity: "info" | "success" | "warning" | "security"
  title: string
  body: string | null
  link: string | null
  read: boolean
  created_at: string
}

export type NotificationPage = {
  items: AppNotification[]
  unread: number
  next_before_id: number | null
}

export async function fetchNotifications(limit = 20): Promise<NotificationPage> {
  const { data } = await api.get("/notifications", { params: { limit } })

  return data as NotificationPage
}

export async function fetchUnreadCount(): Promise<number> {
  const { data } = await api.get("/notifications/unread-count")

  return Number(data?.unread) || 0
}

export async function markNotificationRead(id: number): Promise<void> {
  await api.post(`/notifications/${id}/read`)
}

export async function markAllNotificationsRead(): Promise<void> {
  await api.post("/notifications/read-all")
}

/** Only links that stay inside the app are followed. */
export function safeLink(link: string | null | undefined): string | null {
  const value = (link ?? "").trim()

  if (
    !value ||
    !value.startsWith("/") ||
    value.startsWith("//") ||
    value.includes("\\")
  ) {
    return null
  }

  return value
}

/** The server sends UTC times without a zone marker, so one is added. */
export function parseServerTime(iso: string): number {
  const hasZone = /[zZ]$|[+-]\d\d:?\d\d$/.test(iso)

  return Date.parse(hasZone ? iso : `${iso}Z`)
}

export function timeAgo(iso: string, now: number = Date.now()): string {
  const then = parseServerTime(iso)

  if (Number.isNaN(then)) {
    return ""
  }

  const seconds = Math.max(0, Math.round((now - then) / 1000))

  if (seconds < 45) return "just now"

  const minutes = Math.round(seconds / 60)

  if (minutes < 60) return `${minutes} min ago`

  const hours = Math.round(minutes / 60)

  if (hours < 24) return `${hours} h ago`

  const days = Math.round(hours / 24)

  if (days < 7) return `${days} d ago`

  return new Date(then).toLocaleDateString()
}
