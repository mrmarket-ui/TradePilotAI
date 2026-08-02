import {
  NavLink,
  Outlet,
} from "react-router-dom"

import {
  BarChart3,
  BrainCircuit,
  Building2,
  ChartNoAxesCombined,
  CreditCard,
  FileText,
  FlaskConical,
  LayoutDashboard,
  LockKeyhole,
  LogOut,
  Settings,
  ShieldCheck,
  Sparkles,
  Target,
  WalletCards,
} from "lucide-react"

import { useAuth } from "@/Auth"
import { useTranslation } from "react-i18next"


const standardItems = [
  ["/dashboard", "Dashboard", LayoutDashboard],
  ["/trades", "Trade Journal", WalletCards],
  ["/analytics", "Analytics", BarChart3],
  ["/trader-dna", "Trader DNA", BrainCircuit],
  ["/coach", "AI Coach", Sparkles],
] as const


const premiumItems = [
  [
    "/strategy-lab",
    "Strategy Lab",
    FlaskConical,
  ],
  [
    "/setup-scorer",
    "Setup Scorer",
    Target,
  ],
] as const


const remainingItems = [
  ["/reports", "Reports", FileText],
  [
    "/partners",
    "Brokers & Partners",
    Building2,
  ],
  ["/billing", "Billing", CreditCard],
  ["/settings", "Settings", Settings],
] as const


export default function Shell() {
  const {
    user,
    logout,
  } = useAuth()

  const name =
    user?.full_name ||
    user?.username ||
    user?.email ||
    "Trader"

  const plan =
    user?.plan?.toLowerCase() ||
    "free"

  const hasPremium =
    Boolean(user?.is_admin) ||
    plan === "premium"

  const navClass = ({
    isActive,
  }: {
    isActive: boolean
  }) =>
    [
      "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition",
      isActive
        ? "bg-blue-500/15 text-blue-300"
        : "text-slate-400 hover:bg-white/[0.04] hover:text-white",
    ].join(" ")

  return (
    <div className="min-h-screen bg-[#060912] text-slate-100">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-white/10 bg-[#080d18]/95 lg:block">
        <div className="flex h-full flex-col">
          <div className="flex h-20 items-center gap-3 px-6">
            <div className="grid size-11 place-items-center rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-700">
              <ChartNoAxesCombined />
            </div>

            <div>
              <b>TradePilot AI</b>

              <p className="text-xs text-slate-500">
                Trading Intelligence
              </p>
            </div>
          </div>

          <nav className="flex-1 space-y-1 overflow-y-auto px-4 pb-4">
            {standardItems.map(
              ([to, label, Icon]) => (
                <NavLink
                  key={to}
                  to={to}
                  className={navClass}
                >
                  <Icon className="size-5 shrink-0" />
                  <span>{label}</span>
                </NavLink>
              ),
            )}

            {premiumItems.map(
              ([to, label, Icon]) => (
                <NavLink
                  key={to}
                  to={
                    hasPremium
                      ? to
                      : "/billing"
                  }
                  className={navClass}
                >
                  <Icon className="size-5 shrink-0" />

                  <span className="flex-1">
                    {label}
                  </span>

                  {!hasPremium ? (
                    <span className="flex items-center gap-1 rounded-lg bg-indigo-500/10 px-2 py-1 text-[10px] font-medium uppercase tracking-wide text-indigo-300">
                      <LockKeyhole className="size-3" />
                      Premium
                    </span>
                  ) : null}
                </NavLink>
              ),
            )}

            {remainingItems.map(
              ([to, label, Icon]) => (
                <NavLink
                  key={to}
                  to={to}
                  className={navClass}
                >
                  <Icon className="size-5 shrink-0" />
                  <span>{label}</span>
                </NavLink>
              ),
            )}

            {user?.is_admin ? (
              <>
                <div className="my-4 border-t border-white/10" />

                <NavLink
                  to="/admin"
                  className={navClass}
                >
                  <ShieldCheck className="size-5 shrink-0" />

                  <span>Admin</span>
                </NavLink>
              </>
            ) : null}
          </nav>

          <div className="mx-4 mb-2 rounded-2xl border border-white/10 bg-white/[0.02] p-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Current plan
            </p>

            <p className="mt-1 font-semibold capitalize">
              {user?.is_admin
                ? "Owner · Premium"
                : plan}
            </p>
          </div>

          <button
            type="button"
            onClick={logout}
            className="m-4 mt-2 flex items-center gap-3 rounded-2xl px-4 py-3 text-slate-400 transition hover:bg-white/[0.04] hover:text-white"
          >
            <LogOut className="size-5" />
            Sign out
          </button>
        </div>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-20 border-b border-white/10 bg-[#060912]/80 backdrop-blur-xl">
          <div className="flex h-20 items-center justify-between px-6">
            <div>
              <p className="text-sm text-slate-500">
                Welcome back
              </p>

              <h1 className="text-xl font-semibold">
                {name}
              </h1>
            </div>

            <div className="grid size-11 place-items-center rounded-2xl bg-blue-500 font-semibold">
              {String(name)
                .slice(0, 2)
                .toUpperCase()}
            </div>
          </div>
        </header>

        <main className="px-4 py-5 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
