import {
  Activity,
  BrainCircuit,
  CheckCircle2,
  CircleDollarSign,
  Clock3,
  Percent,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingDown,
  TrendingUp,
  WalletCards,
} from "lucide-react"

import { useQuery } from "@tanstack/react-query"

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import { dashboard } from "@/api"


type DashboardPayload = {
  summary?: {
    total_trades?: number
    wins?: number
    losses?: number
    win_rate?: number
    net_profit?: number
    gross_profit?: number
    gross_loss?: number
    average_profit?: number
    best_trade?: number
    worst_trade?: number
    profit_factor?: number
  }

  overview?: {
    today_profit?: number
    today_trades?: number
    consistency_score?: number
    discipline_score?: number
    confidence_score?: number
    risk_limit_percent?: number | null
    approval_required?: boolean

    current_strategy?: {
      id?: number
      name?: string
      description?: string | null
      markets?: string[]
      sessions?: string[]
      timeframes?: string[]
      entry_rules?: string[]
      confirmations?: string[]
      max_risk_percent?: number
      max_trades_per_day?: number
      requires_user_approval?: boolean
    } | null
  }

  active_strategy?: {
    id?: number
    name?: string
    description?: string | null
    markets?: string[]
    sessions?: string[]
    timeframes?: string[]
    entry_rules?: string[]
    confirmations?: string[]
    max_risk_percent?: number
    max_trades_per_day?: number
    requires_user_approval?: boolean
  } | null

  intelligence?: {
    headline?: {
      title?: string
      message?: string
    }

    mission?: {
      today?: string
      this_week?: string
    }

    scorecard?: {
      overall?: number
      consistency?: number
      risk?: number
      psychology?: number
      discipline?: number
    }
  }

  equity_curve?: Array<{
    date: string
    balance: number
  }>

  recent_trades?: Array<{
    id: number
    pair: string
    direction: string
    profit: number
    lot_size?: number | null
    strategy?: string | null
    opened_at?: string | null
    closed_at?: string | null
  }>

  recommendations?: Array<{
    title?: string
    message?: string
    category?: string
    priority?: string
    action?: string
  }>

  trader_dna?: {
    profile?: string
    overall_score?: number
    strengths?: string[]
    weaknesses?: string[]
  }

  generated_at?: string
}


function money(value?: number) {
  return new Intl.NumberFormat(
    "en-US",
    {
      style: "currency",
      currency: "USD",
    },
  ).format(value || 0)
}


function StatCard({
  label,
  value,
  helper,
  icon: Icon,
  tone = "blue",
}: {
  label: string
  value: string
  helper: string
  icon: typeof TrendingUp
  tone?: "blue" | "green" | "red" | "amber"
}) {
  const toneClasses = {
    blue: "bg-blue-400/10 text-blue-300",
    green: "bg-emerald-400/10 text-emerald-300",
    red: "bg-red-400/10 text-red-300",
    amber: "bg-amber-400/10 text-amber-300",
  }

  return (
    <article className="premium-card rounded-3xl p-5 transition duration-300 hover:-translate-y-1">
      <div
        className={[
          "grid size-11 place-items-center rounded-2xl",
          toneClasses[tone],
        ].join(" ")}
      >
        <Icon className="size-5" />
      </div>

      <p className="mt-5 text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-3xl font-semibold tracking-tight">
        {value}
      </p>

      <p className="mt-2 text-xs leading-5 text-slate-500">
        {helper}
      </p>
    </article>
  )
}


function LoadingDashboard() {
  return (
    <div className="space-y-6">
      <div className="premium-card h-64 animate-pulse rounded-[2rem]" />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div
            key={index}
            className="premium-card h-44 animate-pulse rounded-3xl"
          />
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.5fr_0.7fr]">
        <div className="premium-card h-96 animate-pulse rounded-[2rem]" />
        <div className="premium-card h-96 animate-pulse rounded-[2rem]" />
      </div>
    </div>
  )
}


export default function DashboardPage() {
  const query = useQuery<DashboardPayload>({
    queryKey: ["dashboard"],
    queryFn: dashboard,
    refetchInterval: 60_000,
  })

  if (query.isLoading) {
    return <LoadingDashboard />
  }

  if (query.isError) {
    return (
      <div className="premium-card rounded-[2rem] p-8">
        <p className="text-lg font-semibold text-red-300">
          Dashboard unavailable
        </p>

        <p className="mt-2 text-sm text-slate-400">
          Confirm that the backend is running, then retry.
        </p>

        <button
          type="button"
          onClick={() => query.refetch()}
          className="mt-5 rounded-2xl bg-blue-500 px-5 py-3 text-sm font-semibold"
        >
          Retry dashboard
        </button>
      </div>
    )
  }

  const data = query.data || {}
  const summary = data.summary || {}
  const overview = data.overview || {}
  const intelligence = data.intelligence || {}
  const strategy =
    data.active_strategy ||
    overview.current_strategy ||
    null

  const equityCurve = data.equity_curve || []
  const recentTrades = data.recent_trades || []
  const recommendations =
    data.recommendations || []

  const todayProfit =
    overview.today_profit || 0

  const profitTone =
    todayProfit >= 0 ? "green" : "red"

  const strategyRules =
    strategy?.entry_rules?.slice(0, 4) || []

  const strategyConfirmations =
    strategy?.confirmations?.slice(0, 3) || []

  return (
    <div className="space-y-6">
      <section className="premium-card grid-surface relative overflow-hidden rounded-[2rem] p-6 sm:p-8">
        <div className="absolute right-0 top-0 size-72 rounded-full bg-blue-500/10 blur-3xl" />

        <div className="relative grid gap-8 xl:grid-cols-[1.4fr_0.6fr] xl:items-end">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-blue-300">
                AI performance brief
              </p>

              <span className="flex items-center gap-2 rounded-full border border-emerald-400/15 bg-emerald-400/[0.06] px-3 py-1 text-xs font-semibold text-emerald-300">
                <Sparkles className="size-3.5" />
                Intelligence active
              </span>
            </div>

            <h2 className="mt-5 max-w-4xl text-3xl font-semibold tracking-tight sm:text-4xl xl:text-5xl">
              {intelligence.headline?.title ||
                "Your trading intelligence is ready."}
            </h2>

            <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-400 sm:text-base">
              {intelligence.headline?.message ||
                "TradePilot AI is analyzing your performance, strategy discipline and risk behaviour."}
            </p>
          </div>

          <div className="rounded-3xl border border-white/[0.08] bg-black/20 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Today’s mission
            </p>

            <p className="mt-3 text-xl font-semibold">
              {intelligence.mission?.today ||
                "Follow only your highest-quality setup."}
            </p>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              {intelligence.mission?.this_week ||
                "Protect capital and follow your active strategy."}
            </p>
          </div>
        </div>
      </section>


      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Today’s P&L"
          value={money(todayProfit)}
          helper={`${overview.today_trades || 0} trades recorded today`}
          icon={
            todayProfit >= 0
              ? TrendingUp
              : TrendingDown
          }
          tone={profitTone}
        />

        <StatCard
          label="Win rate"
          value={`${summary.win_rate || 0}%`}
          helper={`${summary.wins || 0} wins from ${summary.total_trades || 0} trades`}
          icon={Percent}
          tone="blue"
        />

        <StatCard
          label="Profit factor"
          value={String(
            summary.profit_factor || 0,
          )}
          helper="Gross profit divided by gross loss"
          icon={Activity}
          tone="green"
        />

        <StatCard
          label="Trader DNA"
          value={
            data.trader_dna?.profile ||
            `${intelligence.scorecard?.overall || 0}/100`
          }
          helper={`Consistency ${overview.consistency_score || 0}/100`}
          icon={BrainCircuit}
          tone="amber"
        />
      </section>


      <section className="grid gap-6 xl:grid-cols-[1.45fr_0.75fr]">
        <article className="premium-card rounded-[2rem] p-5 sm:p-6">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-blue-300">
                Performance
              </p>

              <h3 className="mt-2 text-xl font-semibold">
                Equity curve
              </h3>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-2 text-sm">
              Net profit{" "}
              <strong
                className={
                  (summary.net_profit || 0) >= 0
                    ? "text-emerald-300"
                    : "text-red-300"
                }
              >
                {money(summary.net_profit)}
              </strong>
            </div>
          </div>

          <div className="mt-6 h-80">
            {equityCurve.length ? (
              <ResponsiveContainer
                width="100%"
                height="100%"
              >
                <AreaChart data={equityCurve}>
                  <defs>
                    <linearGradient
                      id="dashboard-equity"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop
                        offset="0%"
                        stopColor="#5c7cff"
                        stopOpacity={0.45}
                      />

                      <stop
                        offset="100%"
                        stopColor="#5c7cff"
                        stopOpacity={0}
                      />
                    </linearGradient>
                  </defs>

                  <CartesianGrid
                    stroke="rgba(148,163,184,.08)"
                    vertical={false}
                  />

                  <XAxis
                    dataKey="date"
                    stroke="#64748b"
                    tickLine={false}
                    axisLine={false}
                    minTickGap={40}
                    tickFormatter={(value) =>
                      new Date(value).toLocaleDateString(
                        undefined,
                        {
                          month: "short",
                          day: "numeric",
                        },
                      )
                    }
                  />

                  <YAxis
                    stroke="#64748b"
                    tickLine={false}
                    axisLine={false}
                  />

                  <Tooltip
                    formatter={(value) =>
                      money(Number(value))
                    }
                    labelFormatter={(value) =>
                      new Date(value).toLocaleString()
                    }
                    contentStyle={{
                      background: "#0b1120",
                      border:
                        "1px solid rgba(148,163,184,.15)",
                      borderRadius: "16px",
                    }}
                  />

                  <Area
                    type="monotone"
                    dataKey="balance"
                    stroke="#6d8dff"
                    strokeWidth={3}
                    fill="url(#dashboard-equity)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="grid h-full place-items-center rounded-3xl border border-dashed border-white/10">
                <div className="text-center">
                  <TrendingUp className="mx-auto size-8 text-slate-600" />

                  <p className="mt-3 text-sm text-slate-500">
                    Add closed trades to build your
                    equity curve.
                  </p>
                </div>
              </div>
            )}
          </div>
        </article>


        <article className="premium-card rounded-[2rem] p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-blue-300">
                Active strategy
              </p>

              <h3 className="mt-2 text-2xl font-semibold">
                {strategy?.name ||
                  "No strategy active"}
              </h3>
            </div>

            <div className="grid size-12 place-items-center rounded-2xl bg-blue-400/10 text-blue-300">
              <Target className="size-6" />
            </div>
          </div>

          <p className="mt-4 text-sm leading-6 text-slate-400">
            {strategy?.description ||
              "Activate a Strategy Brain profile to receive personalized setup scoring."}
          </p>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <div className="rounded-2xl bg-white/[0.03] p-4">
              <p className="text-xs text-slate-500">
                Maximum risk
              </p>

              <p className="mt-2 text-xl font-semibold">
                {strategy?.max_risk_percent ??
                  overview.risk_limit_percent ??
                  0}
                %
              </p>
            </div>

            <div className="rounded-2xl bg-white/[0.03] p-4">
              <p className="text-xs text-slate-500">
                Trades per day
              </p>

              <p className="mt-2 text-xl font-semibold">
                {strategy?.max_trades_per_day ||
                  "—"}
              </p>
            </div>
          </div>

          <div className="mt-6 space-y-2">
            {[...strategyRules, ...strategyConfirmations]
              .slice(0, 5)
              .map((rule) => (
                <div
                  key={rule}
                  className="flex items-start gap-3 rounded-2xl border border-white/[0.06] bg-white/[0.025] px-4 py-3"
                >
                  <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-300" />

                  <span className="text-sm text-slate-300">
                    {rule}
                  </span>
                </div>
              ))}
          </div>

          <div className="mt-5 flex items-center gap-2 rounded-2xl border border-emerald-400/15 bg-emerald-400/[0.05] px-4 py-3 text-sm text-emerald-300">
            <ShieldCheck className="size-4" />

            {overview.approval_required
              ? "User approval required"
              : "Approval protection disabled"}
          </div>
        </article>
      </section>


      <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <article className="premium-card rounded-[2rem] p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-blue-300">
                AI recommendations
              </p>

              <h3 className="mt-2 text-xl font-semibold">
                What to improve next
              </h3>
            </div>

            <BrainCircuit className="size-6 text-blue-300" />
          </div>

          <div className="mt-5 space-y-3">
            {recommendations.length ? (
              recommendations
                .slice(0, 5)
                .map((item, index) => (
                  <div
                    key={`${item.title || "recommendation"}-${index}`}
                    className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4"
                  >
                    <p className="font-medium">
                      {item.title ||
                        item.category ||
                        `Recommendation ${index + 1}`}
                    </p>

                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      {item.message ||
                        item.action ||
                        "Review this performance area."}
                    </p>
                  </div>
                ))
            ) : (
              <div className="rounded-2xl border border-dashed border-white/10 p-8 text-center text-sm text-slate-500">
                More trades are needed before personalized
                recommendations can be generated.
              </div>
            )}
          </div>
        </article>


        <article className="premium-card rounded-[2rem] p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-blue-300">
                Recent activity
              </p>

              <h3 className="mt-2 text-xl font-semibold">
                Latest trades
              </h3>
            </div>

            <WalletCards className="size-6 text-blue-300" />
          </div>

          <div className="mt-5 space-y-3">
            {recentTrades.length ? (
              recentTrades
                .slice(0, 6)
                .map((trade) => (
                  <div
                    key={trade.id}
                    className="flex items-center justify-between gap-4 rounded-2xl border border-white/[0.07] bg-white/[0.025] px-4 py-3"
                  >
                    <div>
                      <p className="font-medium">
                        {trade.pair}
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        {trade.direction} ·{" "}
                        {trade.strategy ||
                          "Unspecified strategy"}
                      </p>
                    </div>

                    <p
                      className={[
                        "font-semibold",
                        trade.profit >= 0
                          ? "text-emerald-300"
                          : "text-red-300",
                      ].join(" ")}
                    >
                      {money(trade.profit)}
                    </p>
                  </div>
                ))
            ) : (
              <div className="rounded-2xl border border-dashed border-white/10 p-8 text-center text-sm text-slate-500">
                Your latest trades will appear here.
              </div>
            )}
          </div>
        </article>
      </section>


      <section className="grid gap-4 md:grid-cols-3">
        <div className="premium-card rounded-3xl p-5">
          <div className="flex items-center gap-3">
            <Clock3 className="size-5 text-blue-300" />

            <p className="font-medium">
              Data freshness
            </p>
          </div>

          <p className="mt-3 text-sm text-slate-400">
            {data.generated_at
              ? `Updated ${new Date(
                  data.generated_at,
                ).toLocaleString()}`
              : "Live dashboard data"}
          </p>
        </div>

        <div className="premium-card rounded-3xl p-5">
          <div className="flex items-center gap-3">
            <CircleDollarSign className="size-5 text-amber-300" />

            <p className="font-medium">
              Current plan
            </p>
          </div>

          <p className="mt-3 text-xl font-semibold text-amber-300">
            Premium · $29.99/month
          </p>
        </div>

        <div className="premium-card rounded-3xl p-5">
          <div className="flex items-center gap-3">
            <ShieldCheck className="size-5 text-emerald-300" />

            <p className="font-medium">
              Risk protection
            </p>
          </div>

          <p className="mt-3 text-xl font-semibold text-emerald-300">
            {overview.discipline_score || 0}/100
          </p>
        </div>
      </section>
    </div>
  )
}
