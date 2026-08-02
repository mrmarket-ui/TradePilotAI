import { useQuery } from "@tanstack/react-query"
import {
  Activity,
  CreditCard,
  ShieldCheck,
  Users,
  WalletCards,
} from "lucide-react"

import {
  getAdminOverview,
} from "@/api/admin/admin"

function Card({
  title,
  value,
  subtitle,
  Icon,
}: {
  title: string
  value: string | number
  subtitle?: string
  Icon: typeof Users
}) {
  return (
    <div className="premium-card rounded-3xl p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">
            {title}
          </p>

          <p className="mt-3 text-3xl font-semibold">
            {value}
          </p>

          {subtitle ? (
            <p className="mt-2 text-xs text-slate-500">
              {subtitle}
            </p>
          ) : null}
        </div>

        <div className="grid size-12 place-items-center rounded-2xl bg-blue-500/10 text-blue-300">
          <Icon className="size-5" />
        </div>
      </div>
    </div>
  )
}

export default function AdminDashboard() {
  const query = useQuery({
    queryKey: ["admin-overview"],
    queryFn: getAdminOverview,
  })

  if (query.isLoading) {
    return (
      <div className="py-10 text-slate-400">
        Loading admin dashboard...
      </div>
    )
  }

  if (query.isError || !query.data) {
    return (
      <div className="rounded-3xl border border-red-400/20 bg-red-400/10 p-6 text-red-300">
        Unable to load admin dashboard.
      </div>
    )
  }

  const data = query.data

  return (
    <div>
      <div>
        <p className="text-xs uppercase tracking-[0.25em] text-blue-300">
          Admin Control Center
        </p>

        <h1 className="mt-3 text-3xl font-semibold">
          Platform Overview
        </h1>

        <p className="mt-2 text-slate-500">
          Monitor users, subscriptions and system activity.
        </p>
      </div>

      <div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <Card
          title="Total Users"
          value={data.users.total}
          subtitle={`${data.users.active} active`}
          Icon={Users}
        />

        <Card
          title="Active Subscriptions"
          value={data.subscriptions.active}
          subtitle={`${data.subscriptions.pending} pending`}
          Icon={CreditCard}
        />

        <Card
          title="Total Trades"
          value={data.trades.total}
          Icon={WalletCards}
        />

        <Card
          title="System Status"
          value={data.system.status}
          Icon={Activity}
        />
      </div>

      <div className="mt-8 grid gap-5 md:grid-cols-2">
        <div className="premium-card rounded-3xl p-6">
          <div className="flex items-center gap-3">
            <ShieldCheck className="size-5 text-blue-300" />
            <h2 className="text-xl font-semibold">
              Plan Distribution
            </h2>
          </div>

          <div className="mt-6 space-y-4">
            <div className="flex justify-between">
              <span className="text-slate-400">
                Pro
              </span>
              <span>{data.users.pro}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-400">
                Premium
              </span>
              <span>{data.users.premium}</span>
            </div>
          </div>
        </div>

        <div className="premium-card rounded-3xl p-6">
          <h2 className="text-xl font-semibold">
            Administrator
          </h2>

          <p className="mt-4 text-slate-400">
            {data.admin.email}
          </p>

          <p className="mt-2 text-sm text-slate-500">
            Admin ID: {data.admin.id}
          </p>
        </div>
      </div>
    </div>
  )
}
