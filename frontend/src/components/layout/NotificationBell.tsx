import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  Bell,
  CheckCheck,
  CircleCheck,
  Info,
  ShieldAlert,
  TriangleAlert,
} from "lucide-react"

import {
  fetchNotifications,
  fetchUnreadCount,
  markAllNotificationsRead,
  markNotificationRead,
  safeLink,
  timeAgo,
  type AppNotification,
} from "@/api/notifications"

const ICONS = {
  info: { Icon: Info, className: "text-blue-300" },
  success: { Icon: CircleCheck, className: "text-emerald-300" },
  warning: { Icon: TriangleAlert, className: "text-amber-300" },
  security: { Icon: ShieldAlert, className: "text-rose-300" },
} as const

export default function NotificationBell() {
  const [open, setOpen] = useState(false)
  const container = useRef<HTMLDivElement | null>(null)
  const button = useRef<HTMLButtonElement | null>(null)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const count = useQuery({
    queryKey: ["notifications", "count"],
    queryFn: fetchUnreadCount,
    refetchInterval: 60_000,
    refetchIntervalInBackground: false,
    staleTime: 30_000,
  })

  const list = useQuery({
    queryKey: ["notifications", "list"],
    queryFn: () => fetchNotifications(20),
    enabled: open,
    staleTime: 0,
  })

  const refresh = () =>
    queryClient.invalidateQueries({ queryKey: ["notifications"] })

  const markOne = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: refresh,
  })

  const markAll = useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: refresh,
  })

  useEffect(() => {
    if (!open) {
      return
    }

    function onPointerDown(event: MouseEvent) {
      if (!container.current?.contains(event.target as Node)) {
        setOpen(false)
      }
    }

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpen(false)
        button.current?.focus()
      }
    }

    document.addEventListener("mousedown", onPointerDown)
    document.addEventListener("keydown", onKeyDown)

    return () => {
      document.removeEventListener("mousedown", onPointerDown)
      document.removeEventListener("keydown", onKeyDown)
    }
  }, [open])

  const unread = count.data ?? 0
  const badge = unread > 9 ? "9+" : String(unread)

  function openItem(item: AppNotification) {
    if (!item.read) {
      markOne.mutate(item.id)
    }

    const target = safeLink(item.link)

    if (target) {
      setOpen(false)
      navigate(target)
    }
  }

  return (
    <div ref={container} className="relative">
      <button
        ref={button}
        type="button"
        onClick={() => setOpen((current) => !current)}
        className="relative grid size-11 place-items-center rounded-2xl border border-white/10 bg-white/[0.03] text-slate-300 transition hover:bg-white/[0.06]"
        aria-label={
          unread > 0 ? `Notifications, ${unread} unread` : "Notifications"
        }
        aria-haspopup="dialog"
        aria-expanded={open}
      >
        <Bell className="size-5" />

        {unread > 0 && (
          <span
            data-testid="notification-badge"
            className="absolute -right-1 -top-1 grid min-w-5 place-items-center rounded-full bg-blue-500 px-1 text-[10px] font-semibold leading-5 text-white"
          >
            {badge}
          </span>
        )}
      </button>

      {open && (
        <div
          role="dialog"
          aria-label="Notifications"
          className="absolute right-0 top-full z-50 mt-3 w-[min(24rem,calc(100vw-2rem))] overflow-hidden rounded-3xl border border-white/10 bg-[#0b1120] shadow-2xl shadow-black/50"
        >
          <div className="flex items-center justify-between gap-3 border-b border-white/[0.08] px-5 py-4">
            <h2 className="text-sm font-semibold text-slate-100">
              Notifications
            </h2>

            <button
              type="button"
              onClick={() => markAll.mutate()}
              disabled={unread === 0 || markAll.isPending}
              className="flex items-center gap-1.5 text-xs font-medium text-blue-300 disabled:cursor-not-allowed disabled:text-slate-600"
            >
              <CheckCheck className="size-3.5" aria-hidden="true" />
              Mark all read
            </button>
          </div>

          <div className="max-h-[60vh] overflow-y-auto">
            {list.isPending && (
              <p className="px-5 py-8 text-center text-sm text-slate-500">
                Loading...
              </p>
            )}

            {list.isError && (
              <div className="px-5 py-8 text-center text-sm text-slate-400">
                <p>Could not load notifications.</p>

                <button
                  type="button"
                  onClick={() => list.refetch()}
                  className="mt-3 text-blue-300 underline"
                >
                  Try again
                </button>
              </div>
            )}

            {list.isSuccess && list.data.items.length === 0 && (
              <p className="px-5 py-10 text-center text-sm text-slate-500">
                You are all caught up.
              </p>
            )}

            {list.isSuccess &&
              list.data.items.map((item) => {
                const { Icon, className } = ICONS[item.severity] ?? ICONS.info

                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => openItem(item)}
                    className="flex w-full items-start gap-3 border-b border-white/[0.05] px-5 py-4 text-left transition last:border-b-0 hover:bg-white/[0.03]"
                  >
                    <Icon
                      className={`mt-0.5 size-4 shrink-0 ${className}`}
                      aria-hidden="true"
                    />

                    <span className="min-w-0 flex-1">
                      <span
                        className={`block text-sm ${
                          item.read
                            ? "font-medium text-slate-400"
                            : "font-semibold text-slate-100"
                        }`}
                      >
                        {item.title}
                      </span>

                      {item.body && (
                        <span className="mt-1 line-clamp-3 block text-xs leading-5 text-slate-500">
                          {item.body}
                        </span>
                      )}

                      <span className="mt-1.5 block text-[11px] text-slate-600">
                        {timeAgo(item.created_at)}
                      </span>
                    </span>

                    {!item.read && (
                      <span
                        className="mt-1.5 size-2 shrink-0 rounded-full bg-blue-400"
                        aria-label="Unread"
                      />
                    )}
                  </button>
                )
              })}
          </div>
        </div>
      )}
    </div>
  )
}
