import { Menu } from "lucide-react"

import { useAuth } from "@/Auth"
import NotificationBell from "@/components/layout/NotificationBell"

type TopbarProps = {
  userName: string
  onOpenNavigation: () => void
}

// The badge shows the plan the account really has.
const PLAN_BADGE: Record<string, { label: string; className: string }> = {
  free: {
    label: "FREE",
    className: "border-slate-400/20 bg-slate-400/[0.07] text-slate-300",
  },
  pro: {
    label: "PRO",
    className: "border-blue-400/20 bg-blue-400/[0.07] text-blue-300",
  },
  premium: {
    label: "PREMIUM",
    className: "border-amber-400/20 bg-amber-400/[0.07] text-amber-300",
  },
}

export default function Topbar({
  userName,
  onOpenNavigation,
}: TopbarProps) {
  const { user } = useAuth()

  const badge = PLAN_BADGE[(user?.plan ?? "").toLowerCase()]

  const initials = userName
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase()

  return (
    <header className="sticky top-0 z-30 border-b border-white/[0.08] bg-[#060912]/80 backdrop-blur-xl">
      <div className="flex h-20 items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onOpenNavigation}
            className="grid size-11 place-items-center rounded-2xl border border-white/10 bg-white/[0.03] text-slate-300 lg:hidden"
            aria-label="Open navigation"
          >
            <Menu className="size-5" />
          </button>

          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-600">
              Welcome back
            </p>

            <h1 className="mt-1 text-lg font-semibold sm:text-xl">
              {userName}
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <NotificationBell />

          {badge && (
            <div
              className={`hidden rounded-full border px-3 py-1.5 text-xs font-semibold sm:block ${badge.className}`}
            >
              {badge.label}
            </div>
          )}

          <div className="grid size-11 place-items-center rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 text-sm font-semibold text-white shadow-lg shadow-blue-500/20">
            {initials || "TP"}
          </div>
        </div>
      </div>
    </header>
  )
}
