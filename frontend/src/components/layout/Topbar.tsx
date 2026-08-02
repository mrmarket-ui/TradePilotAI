import {
  Bell,
  Menu,
  Search,
  Sparkles,
} from "lucide-react"

type TopbarProps = {
  userName: string
  onOpenNavigation: () => void
}

export default function Topbar({
  userName,
  onOpenNavigation,
}: TopbarProps) {
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
          <label className="hidden items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.03] px-4 md:flex">
            <Search className="size-4 text-slate-500" />

            <input
              type="search"
              placeholder="Search TradePilot..."
              className="w-48 bg-transparent py-2.5 text-sm outline-none placeholder:text-slate-600 xl:w-64"
            />
          </label>

          <div className="hidden items-center gap-2 rounded-full border border-emerald-400/15 bg-emerald-400/[0.06] px-3 py-1.5 text-xs font-semibold text-emerald-300 sm:flex">
            <Sparkles className="size-3.5" />
            AI Online
          </div>

          <button
            type="button"
            className="relative grid size-11 place-items-center rounded-2xl border border-white/10 bg-white/[0.03] text-slate-300"
          >
            <Bell className="size-5" />

            <span className="absolute right-2 top-2 size-2 rounded-full bg-blue-400" />
          </button>

          <div className="hidden rounded-full border border-amber-400/20 bg-amber-400/[0.07] px-3 py-1.5 text-xs font-semibold text-amber-300 sm:block">
            PREMIUM
          </div>

          <div className="grid size-11 place-items-center rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 text-sm font-semibold text-white shadow-lg shadow-blue-500/20">
            {initials || "TP"}
          </div>
        </div>
      </div>
    </header>
  )
}
