import {
  BarChart3,
  BrainCircuit,
  Building2,
  ChartNoAxesCombined,
  CreditCard,
  FileText,
  FlaskConical,
  LayoutDashboard,
  LogOut,
  Settings,
  Sparkles,
  WalletCards,
  X,
} from "lucide-react"
import { NavLink } from "react-router-dom"

type SidebarProps = {
  mobileOpen: boolean
  onClose: () => void
  onLogout: () => void
}

const navigation = [
  {
    title: "Trading",
    items: [
      {
        path: "/dashboard",
        label: "Dashboard",
        icon: LayoutDashboard,
      },
      {
        path: "/trades",
        label: "Trade Journal",
        icon: WalletCards,
      },
      {
        path: "/strategy-lab",
        label: "Strategy Brain",
        icon: FlaskConical,
      },
      {
        path: "/coach",
        label: "AI Coach",
        icon: Sparkles,
      },
      {
        path: "/analytics",
        label: "Analytics",
        icon: BarChart3,
      },
      {
        path: "/trader-dna",
        label: "Trader DNA",
        icon: BrainCircuit,
      },
      {
        path: "/reports",
        label: "Reports",
        icon: FileText,
      },
    ],
  },
  {
    title: "Business",
    items: [
      {
        path: "/partners",
        label: "Brokers & Partners",
        icon: Building2,
      },
    ],
  },
  {
    title: "Account",
    items: [
      {
        path: "/billing",
        label: "Subscription",
        icon: CreditCard,
      },
      {
        path: "/settings",
        label: "Settings",
        icon: Settings,
      },
    ],
  },
]

function SidebarContent({
  onClose,
  onLogout,
}: Pick<SidebarProps, "onClose" | "onLogout">) {
  return (
    <div className="flex h-full flex-col">
      <header className="flex h-20 items-center justify-between border-b border-white/[0.07] px-5">
        <div className="flex items-center gap-3">
          <div className="grid size-11 place-items-center rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-700 shadow-lg shadow-blue-500/20">
            <ChartNoAxesCombined className="size-6 text-white" />
          </div>

          <div>
            <p className="font-semibold tracking-tight text-white">
              TradePilot AI
            </p>

            <p className="text-xs text-slate-500">
              AI Trading OS
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="grid size-9 place-items-center rounded-xl border border-white/10 text-slate-400 lg:hidden"
          aria-label="Close navigation"
        >
          <X className="size-4" />
        </button>
      </header>

      <nav className="flex-1 space-y-7 overflow-y-auto px-4 py-5">
        {navigation.map((section) => (
          <section key={section.title}>
            <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-600">
              {section.title}
            </p>

            <div className="space-y-1">
              {section.items.map(
                ({ path, label, icon: Icon }) => (
                  <NavLink
                    key={path}
                    to={path}
                    onClick={onClose}
                    className={({ isActive }) =>
                      [
                        "flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-medium transition",
                        isActive
                          ? "bg-blue-500/12 text-blue-300 ring-1 ring-blue-400/20"
                          : "text-slate-400 hover:bg-white/[0.045] hover:text-white",
                      ].join(" ")
                    }
                  >
                    <Icon className="size-[18px] shrink-0" />
                    <span>{label}</span>
                  </NavLink>
                ),
              )}
            </div>
          </section>
        ))}
      </nav>

      <footer className="space-y-3 border-t border-white/[0.07] p-4">
        <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium text-slate-300">
              System status
            </p>

            <span className="rounded-full bg-emerald-400/10 px-2 py-1 text-[10px] font-semibold text-emerald-300">
              ONLINE
            </span>
          </div>

          <div className="mt-3 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">API</span>
              <span className="text-emerald-300">Online</span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-500">Database</span>
              <span className="text-emerald-300">Online</span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-500">Vision AI</span>
              <span className="text-amber-300">Coming soon</span>
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={onLogout}
          className="flex w-full items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-medium text-slate-400 transition hover:bg-red-400/[0.06] hover:text-red-300"
        >
          <LogOut className="size-[18px]" />
          Sign out
        </button>
      </footer>
    </div>
  )
}

export default function Sidebar({
  mobileOpen,
  onClose,
  onLogout,
}: SidebarProps) {
  return (
    <>
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 border-r border-white/[0.08] bg-[#080d18]/95 backdrop-blur-xl lg:block">
        <SidebarContent
          onClose={onClose}
          onLogout={onLogout}
        />
      </aside>

      {mobileOpen ? (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            type="button"
            onClick={onClose}
            aria-label="Close navigation"
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
          />

          <aside className="relative h-full w-[88%] max-w-72 border-r border-white/10 bg-[#080d18]">
            <SidebarContent
              onClose={onClose}
              onLogout={onLogout}
            />
          </aside>
        </div>
      ) : null}
    </>
  )
}
