import {
  Activity,
  BarChart3,
  BrainCircuit,
  Flame,
  Gauge,
  Percent,
  ShieldAlert,
  Target,
  TrendingDown,
  TrendingUp,
} from "lucide-react"

import {
  useMemo,
  useState,
} from "react"

import {
  useQuery,
} from "@tanstack/react-query"

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import {
  fetchAdvancedAnalytics,
} from "@/api/analytics"

import type {
  PerformanceGroup,
  SymbolPerformance,
} from "@/types/analytics"


type BreakdownTab =
  | "symbol"
  | "session"
  | "strategy"
  | "emotion"


function money(
  value?: number,
) {
  return new Intl.NumberFormat(
    "en-US",
    {
      style: "currency",
      currency: "USD",
    },
  ).format(
    value || 0,
  )
}


function number(
  value?: number,
  digits = 2,
) {
  return Number(
    value || 0,
  ).toFixed(
    digits,
  )
}


function MetricCard({
  label,
  value,
  helper,
  icon: Icon,
  positive,
}: {
  label: string
  value: string
  helper: string
  icon: typeof Activity
  positive?: boolean
}) {
  return (
    <article className="premium-card rounded-3xl p-5 transition duration-300 hover:-translate-y-1">

      <div
        className={[
          "grid size-11 place-items-center rounded-2xl",

          positive === true
            ? "bg-emerald-400/10 text-emerald-300"
            : positive === false
            ? "bg-red-400/10 text-red-300"
            : "bg-blue-400/10 text-blue-300",

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


function PerformanceTable({
  data,
  mode,
}: {
  data: Record<
    string,
    PerformanceGroup | SymbolPerformance
  >
  mode: BreakdownTab
}) {
  const rows =
    Object.entries(
      data,
    )
      .map(
        ([name, stats]) => ({
          name,
          stats,
        }),
      )
      .sort(
        (a, b) => {
          const aProfit =
            "net_profit" in a.stats
              ? a.stats.net_profit
              : a.stats.profit

          const bProfit =
            "net_profit" in b.stats
              ? b.stats.net_profit
              : b.stats.profit

          return (
            Number(
              bProfit || 0,
            ) -
            Number(
              aProfit || 0,
            )
          )
        },
      )

  if (!rows.length) {
    return (
      <div className="rounded-2xl border border-dashed border-white/10 p-10 text-center text-sm text-slate-500">
        More trades are needed before this analysis becomes available.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">

      <table className="w-full min-w-[760px]">

        <thead>
          <tr className="border-b border-white/[0.07]">

            <th className="px-4 py-4 text-left text-xs uppercase tracking-wider text-slate-500">
              {mode}
            </th>

            <th className="px-4 py-4 text-left text-xs uppercase tracking-wider text-slate-500">
              Trades
            </th>

            <th className="px-4 py-4 text-left text-xs uppercase tracking-wider text-slate-500">
              Wins
            </th>

            <th className="px-4 py-4 text-left text-xs uppercase tracking-wider text-slate-500">
              Losses
            </th>

            <th className="px-4 py-4 text-left text-xs uppercase tracking-wider text-slate-500">
              Win Rate
            </th>

            <th className="px-4 py-4 text-left text-xs uppercase tracking-wider text-slate-500">
              Net P&L
            </th>

          </tr>
        </thead>

        <tbody>
          {rows.map(
            ({
              name,
              stats,
            }) => {
              const profit =
                "net_profit" in stats
                  ? stats.net_profit
                  : stats.profit

              return (
                <tr
                  key={name}
                  className="border-b border-white/[0.05]"
                >

                  <td className="px-4 py-4 font-semibold">
                    {name}
                  </td>

                  <td className="px-4 py-4 text-slate-300">
                    {stats.trades}
                  </td>

                  <td className="px-4 py-4 text-emerald-300">
                    {stats.wins}
                  </td>

                  <td className="px-4 py-4 text-red-300">
                    {stats.losses}
                  </td>

                  <td className="px-4 py-4">
                    {number(
                      stats.win_rate,
                      1,
                    )}
                    %
                  </td>

                  <td
                    className={[
                      "px-4 py-4 font-semibold",

                      Number(
                        profit || 0,
                      ) >= 0
                        ? "text-emerald-300"
                        : "text-red-300",

                    ].join(" ")}
                  >
                    {money(
                      Number(
                        profit || 0,
                      ),
                    )}
                  </td>

                </tr>
              )
            },
          )}
        </tbody>

      </table>

    </div>
  )
}


function LoadingAnalytics() {
  return (
    <div className="space-y-6">

      <div className="premium-card h-56 animate-pulse rounded-[2rem]" />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({
          length: 8,
        }).map(
          (_, index) => (
            <div
              key={index}
              className="premium-card h-40 animate-pulse rounded-3xl"
            />
          ),
        )}
      </div>

    </div>
  )
}


export default function AdvancedAnalyticsPage() {
  const [
    tab,
    setTab,
  ] = useState<BreakdownTab>(
    "symbol",
  )

  const query =
    useQuery({
      queryKey: [
        "advanced-analytics",
      ],

      queryFn:
        fetchAdvancedAnalytics,

      refetchInterval:
        60_000,
    })


  const data =
    query.data


  const breakdown =
    useMemo(
      () => {
        if (!data) {
          return {}
        }

        if (
          tab ===
          "symbol"
        ) {
          return data.by_symbol
        }

        if (
          tab ===
          "session"
        ) {
          return data.by_session
        }

        if (
          tab ===
          "strategy"
        ) {
          return data.by_strategy
        }

        return data.by_emotion
      },
      [
        data,
        tab,
      ],
    )


  if (
    query.isLoading
  ) {
    return (
      <LoadingAnalytics />
    )
  }


  if (
    query.isError ||
    !data
  ) {
    return (
      <section className="premium-card rounded-[2rem] p-8">

        <p className="text-xl font-semibold text-red-300">
          Advanced analytics unavailable
        </p>

        <p className="mt-3 text-sm text-slate-400">
          TradePilot AI could not load your advanced trading statistics.
        </p>

        <button
          type="button"
          onClick={() =>
            query.refetch()
          }
          className="mt-5 rounded-2xl bg-blue-500 px-5 py-3 font-semibold"
        >
          Retry
        </button>

      </section>
    )
  }


  const averageR =
    data.r_multiple
      ?.average_r ||
    0

  const maxDrawdown =
    data.drawdown
      ?.max_drawdown ||
    0

  const maxDrawdownPercent =
    data.drawdown
      ?.max_drawdown_percent ||
    0


  return (
    <div className="space-y-6">

      <section className="premium-card grid-surface relative overflow-hidden rounded-[2rem] p-6 sm:p-8">

        <div className="absolute right-0 top-0 size-80 rounded-full bg-indigo-500/10 blur-3xl" />

        <div className="relative">

          <div className="flex items-center gap-3">

            <div className="grid size-11 place-items-center rounded-2xl bg-blue-400/10 text-blue-300">
              <BarChart3 className="size-5" />
            </div>

            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-blue-300">
              TradePilot Intelligence
            </p>

          </div>

          <h1 className="mt-5 max-w-4xl text-3xl font-semibold tracking-tight sm:text-4xl xl:text-5xl">
            Advanced Trading Analytics
          </h1>

          <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-400 sm:text-base">
            Discover where your edge actually comes from.
            Compare strategies, symbols, sessions,
            psychology, expectancy, risk and R-multiple performance.
          </p>

        </div>

      </section>


      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <MetricCard
          label="Net Profit"
          value={
            money(
              data.net_profit,
            )
          }
          helper={`${data.total_trades} total trades`}
          icon={
            data.net_profit >= 0
              ? TrendingUp
              : TrendingDown
          }
          positive={
            data.net_profit >= 0
          }
        />

        <MetricCard
          label="Win Rate"
          value={`${number(
            data.win_rate,
            1,
          )}%`}
          helper={`${data.wins} wins · ${data.losses} losses`}
          icon={Percent}
        />

        <MetricCard
          label="Profit Factor"
          value={
            number(
              data.profit_factor,
              2,
            )
          }
          helper="Gross profit divided by gross loss"
          icon={Activity}
          positive={
            data.profit_factor >= 1
          }
        />

        <MetricCard
          label="Expectancy"
          value={
            money(
              data.expectancy,
            )
          }
          helper="Expected profit per recorded trade"
          icon={Target}
          positive={
            data.expectancy >= 0
          }
        />


        <MetricCard
          label="Average R"
          value={`${number(
            averageR,
            2,
          )}R`}
          helper={`${data.r_multiple?.trades_with_r || 0} trades with usable R data`}
          icon={Gauge}
          positive={
            averageR >= 0
          }
        />

        <MetricCard
          label="Total R"
          value={`${number(
            data.r_multiple?.total_r,
            2,
          )}R`}
          helper={`Best ${number(
            data.r_multiple?.best_r,
            2,
          )}R · Worst ${number(
            data.r_multiple?.worst_r,
            2,
          )}R`}
          icon={BrainCircuit}
          positive={
            (
              data.r_multiple
                ?.total_r ||
              0
            ) >= 0
          }
        />

        <MetricCard
          label="Maximum Drawdown"
          value={
            money(
              maxDrawdown,
            )
          }
          helper={`${number(
            maxDrawdownPercent,
            2,
          )}% peak drawdown`}
          icon={ShieldAlert}
          positive={false}
        />

        <MetricCard
          label="Best Win Streak"
          value={String(
            data.streaks
              ?.max_win_streak ||
            0,
          )}
          helper={`Worst losing streak: ${
            data.streaks
              ?.max_loss_streak ||
            0
          }`}
          icon={Flame}
          positive
        />

      </section>


      <section className="premium-card rounded-[2rem] p-5 sm:p-6">

        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">

          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-blue-300">
              Equity Intelligence
            </p>

            <h2 className="mt-2 text-2xl font-semibold">
              Performance Curve
            </h2>
          </div>

          <div className="flex flex-wrap gap-2">

            <span className="rounded-xl bg-emerald-400/[0.07] px-3 py-2 text-sm text-emerald-300">
              Best trade{" "}
              {money(
                data.best_trade,
              )}
            </span>

            <span className="rounded-xl bg-red-400/[0.07] px-3 py-2 text-sm text-red-300">
              Worst trade{" "}
              {money(
                data.worst_trade,
              )}
            </span>

          </div>

        </div>


        <div className="mt-7 h-[360px]">

          {data.equity_curve?.length ? (
            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <AreaChart
                data={
                  data.equity_curve
                }
              >

                <defs>

                  <linearGradient
                    id="advanced-equity"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >

                    <stop
                      offset="0%"
                      stopColor="#6d8dff"
                      stopOpacity={0.45}
                    />

                    <stop
                      offset="100%"
                      stopColor="#6d8dff"
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
                  minTickGap={35}
                  tickFormatter={(
                    value,
                  ) =>
                    value
                      ? new Date(
                          value,
                        ).toLocaleDateString(
                          undefined,
                          {
                            month:
                              "short",

                            day:
                              "numeric",
                          },
                        )
                      : ""
                  }
                />


                <YAxis
                  stroke="#64748b"
                  tickLine={false}
                  axisLine={false}
                />


                <Tooltip
                  formatter={(
                    value,
                    name,
                  ) => [
                    money(
                      Number(
                        value,
                      ),
                    ),
                    name,
                  ]}
                  labelFormatter={(
                    value,
                  ) =>
                    value
                      ? new Date(
                          value,
                        ).toLocaleString()
                      : ""
                  }
                  contentStyle={{
                    background:
                      "#0b1120",

                    border:
                      "1px solid rgba(148,163,184,.15)",

                    borderRadius:
                      "16px",
                  }}
                />


                <Area
                  type="monotone"
                  dataKey="balance"
                  stroke="#6d8dff"
                  strokeWidth={3}
                  fill="url(#advanced-equity)"
                />

              </AreaChart>

            </ResponsiveContainer>
          ) : (
            <div className="grid h-full place-items-center rounded-3xl border border-dashed border-white/10 text-sm text-slate-500">
              Add closed trades to generate your advanced equity curve.
            </div>
          )}

        </div>

      </section>


      <section className="premium-card rounded-[2rem] p-5 sm:p-6">

        <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">

          <div>

            <p className="text-xs uppercase tracking-[0.2em] text-blue-300">
              Edge Analysis
            </p>

            <h2 className="mt-2 text-2xl font-semibold">
              Performance Breakdown
            </h2>

          </div>


          <div className="flex flex-wrap gap-2">

            {([
              [
                "symbol",
                "Symbols",
              ],

              [
                "session",
                "Sessions",
              ],

              [
                "strategy",
                "Strategies",
              ],

              [
                "emotion",
                "Psychology",
              ],

            ] as const).map(
              ([
                value,
                label,
              ]) => (

                <button
                  key={value}
                  type="button"
                  onClick={() =>
                    setTab(
                      value,
                    )
                  }
                  className={[
                    "rounded-2xl px-4 py-2 text-sm font-medium transition",

                    tab === value
                      ? "bg-blue-500 text-white"
                      : "border border-white/10 bg-white/[0.03] text-slate-400 hover:text-white",

                  ].join(" ")}
                >
                  {label}
                </button>

              ),
            )}

          </div>

        </div>


        <div className="mt-6">

          <PerformanceTable
            data={
              breakdown as Record<
                string,
                PerformanceGroup |
                SymbolPerformance
              >
            }
            mode={tab}
          />

        </div>

      </section>


      <section className="grid gap-6 lg:grid-cols-2">

        <article className="premium-card rounded-3xl p-6">

          <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">
            Strength
          </p>

          <h3 className="mt-3 text-xl font-semibold">
            Best Performance
          </h3>

          <div className="mt-5 space-y-3">

            <div className="rounded-2xl bg-white/[0.03] p-4">
              <p className="text-sm text-slate-500">
                Average winning trade
              </p>

              <p className="mt-2 text-2xl font-semibold text-emerald-300">
                {money(
                  data.average_win,
                )}
              </p>
            </div>

            <div className="rounded-2xl bg-white/[0.03] p-4">
              <p className="text-sm text-slate-500">
                Best R multiple
              </p>

              <p className="mt-2 text-2xl font-semibold text-emerald-300">
                {number(
                  data.r_multiple
                    ?.best_r,
                  2,
                )}
                R
              </p>
            </div>

          </div>

        </article>


        <article className="premium-card rounded-3xl p-6">

          <p className="text-xs uppercase tracking-[0.2em] text-red-300">
            Risk
          </p>

          <h3 className="mt-3 text-xl font-semibold">
            Weakness Exposure
          </h3>

          <div className="mt-5 space-y-3">

            <div className="rounded-2xl bg-white/[0.03] p-4">
              <p className="text-sm text-slate-500">
                Average losing trade
              </p>

              <p className="mt-2 text-2xl font-semibold text-red-300">
                -{money(
                  Math.abs(
                    data.average_loss,
                  ),
                )}
              </p>
            </div>

            <div className="rounded-2xl bg-white/[0.03] p-4">
              <p className="text-sm text-slate-500">
                Worst R multiple
              </p>

              <p className="mt-2 text-2xl font-semibold text-red-300">
                {number(
                  data.r_multiple
                    ?.worst_r,
                  2,
                )}
                R
              </p>
            </div>

          </div>

        </article>

      </section>

    </div>
  )
}
