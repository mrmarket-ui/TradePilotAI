import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Target,
  X,
} from "lucide-react"

import {
  useMemo,
  useState,
} from "react"

import {
  useQuery,
} from "@tanstack/react-query"

import {
  fetchTradingCalendar,
} from "@/api/calendar"

import {
  fetchTrades,
} from "@/api/trades"

import type {
  Trade,
} from "@/types/trade"


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


function getTradeDate(
  trade: Trade,
) {
  const source =
    trade.closed_at ||
    trade.opened_at ||
    trade.created_at

  return source
    ? new Date(
        source,
      )
        .toISOString()
        .slice(
          0,
          10,
        )
    : ""
}


function getSession(
  trade: Trade,
) {
  const source =
    trade.opened_at ||
    trade.created_at

  if (!source) {
    return "Unknown"
  }

  const hour =
    new Date(
      source,
    ).getUTCHours()

  if (
    hour >= 0 &&
    hour < 7
  ) {
    return "Asia"
  }

  if (
    hour >= 7 &&
    hour < 12
  ) {
    return "London"
  }

  if (
    hour >= 12 &&
    hour < 16
  ) {
    return "London / New York"
  }

  if (
    hour >= 16 &&
    hour < 21
  ) {
    return "New York"
  }

  return "After Hours"
}


function calculateR(
  trade: Trade,
) {
  if (
    trade.exit_price == null
  ) {
    return null
  }

  const risk =
    Math.abs(
      trade.entry -
      trade.stop_loss,
    )

  if (
    risk <= 0
  ) {
    return null
  }

  const reward =
    trade.direction ===
    "BUY"
      ? trade.exit_price -
        trade.entry
      : trade.entry -
        trade.exit_price

  return (
    reward /
    risk
  )
}


function DailyTradePanel({
  date,
  trades,
  onClose,
}: {
  date: string
  trades: Trade[]
  onClose: () => void
}) {
  const netProfit =
    trades.reduce(
      (
        total,
        trade,
      ) =>
        total +
        Number(
          trade.profit ||
          0,
        ),
      0,
    )

  const wins =
    trades.filter(
      (trade) =>
        Number(
          trade.profit ||
          0,
        ) > 0,
    ).length

  const losses =
    trades.filter(
      (trade) =>
        Number(
          trade.profit ||
          0,
        ) < 0,
    ).length

  const winRate =
    trades.length
      ? (
          wins /
          trades.length
        ) *
        100
      : 0

  const rValues =
    trades
      .map(
        calculateR,
      )
      .filter(
        (
          value,
        ): value is number =>
          value !== null,
      )

  const totalR =
    rValues.reduce(
      (
        total,
        value,
      ) =>
        total +
        value,
      0,
    )

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/70 backdrop-blur-sm">

      <aside className="h-full w-full max-w-2xl overflow-y-auto border-l border-white/10 bg-[#080d17] p-5 sm:p-8">

        <div className="flex items-start justify-between gap-4">

          <div>

            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-blue-300">
              Daily Review
            </p>

            <h2 className="mt-2 text-2xl font-semibold">
              {new Date(
                `${date}T00:00:00`,
              ).toLocaleDateString(
                undefined,
                {
                  weekday:
                    "long",
                  year:
                    "numeric",
                  month:
                    "long",
                  day:
                    "numeric",
                },
              )}
            </h2>

          </div>


          <button
            type="button"
            onClick={
              onClose
            }
            className="grid size-10 place-items-center rounded-2xl border border-white/10 bg-white/[0.03]"
          >
            <X className="size-5" />
          </button>

        </div>


        <div className="mt-6 grid gap-3 sm:grid-cols-2">

          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.03] p-4">

            <p className="text-xs text-slate-500">
              Net P&L
            </p>

            <p
              className={[
                "mt-2 text-2xl font-semibold",

                netProfit >= 0
                  ? "text-emerald-300"
                  : "text-red-300",

              ].join(" ")}
            >
              {money(
                netProfit,
              )}
            </p>

          </div>


          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.03] p-4">

            <p className="text-xs text-slate-500">
              Win Rate
            </p>

            <p className="mt-2 text-2xl font-semibold">
              {winRate.toFixed(
                1,
              )}
              %
            </p>

          </div>


          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.03] p-4">

            <p className="text-xs text-slate-500">
              Trades
            </p>

            <p className="mt-2 text-2xl font-semibold">
              {trades.length}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              {wins} wins ·{" "}
              {losses} losses
            </p>

          </div>


          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.03] p-4">

            <p className="text-xs text-slate-500">
              Total R
            </p>

            <p
              className={[
                "mt-2 text-2xl font-semibold",

                totalR >= 0
                  ? "text-emerald-300"
                  : "text-red-300",

              ].join(" ")}
            >
              {totalR.toFixed(
                2,
              )}
              R
            </p>

          </div>

        </div>


        <div className="mt-8">

          <div className="flex items-center gap-2">

            <Target className="size-5 text-blue-300" />

            <h3 className="text-lg font-semibold">
              Trades
            </h3>

          </div>


          <div className="mt-4 space-y-3">

            {trades.length ? (
              trades.map(
                (trade) => {
                  const r =
                    calculateR(
                      trade,
                    )

                  const profit =
                    Number(
                      trade.profit ||
                      0,
                    )

                  return (
                    <article
                      key={
                        trade.id
                      }
                      className="rounded-3xl border border-white/[0.07] bg-white/[0.025] p-5"
                    >

                      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">

                        <div>

                          <div className="flex flex-wrap items-center gap-2">

                            <p className="text-lg font-semibold">
                              {trade.pair}
                            </p>

                            <span
                              className={[
                                "rounded-full px-2.5 py-1 text-xs font-semibold",

                                trade.direction ===
                                "BUY"
                                  ? "bg-emerald-400/10 text-emerald-300"
                                  : "bg-red-400/10 text-red-300",

                              ].join(" ")}
                            >
                              {trade.direction}
                            </span>

                          </div>


                          <p className="mt-2 text-sm text-slate-400">
                            {trade.strategy ||
                              "Unspecified strategy"}
                          </p>

                        </div>


                        <p
                          className={[
                            "text-xl font-semibold",

                            profit >= 0
                              ? "text-emerald-300"
                              : "text-red-300",

                          ].join(" ")}
                        >
                          {money(
                            profit,
                          )}
                        </p>

                      </div>


                      <div className="mt-5 grid gap-3 sm:grid-cols-2">

                        <div className="rounded-2xl bg-white/[0.03] p-3">

                          <p className="text-xs text-slate-500">
                            Entry
                          </p>

                          <p className="mt-1 font-medium">
                            {trade.entry}
                          </p>

                        </div>


                        <div className="rounded-2xl bg-white/[0.03] p-3">

                          <p className="text-xs text-slate-500">
                            Exit
                          </p>

                          <p className="mt-1 font-medium">
                            {trade.exit_price ??
                              "Open"}
                          </p>

                        </div>


                        <div className="rounded-2xl bg-white/[0.03] p-3">

                          <p className="text-xs text-slate-500">
                            Session
                          </p>

                          <p className="mt-1 font-medium">
                            {getSession(
                              trade,
                            )}
                          </p>

                        </div>


                        <div className="rounded-2xl bg-white/[0.03] p-3">

                          <p className="text-xs text-slate-500">
                            R Multiple
                          </p>

                          <p className="mt-1 font-medium">
                            {r == null
                              ? "—"
                              : `${r.toFixed(
                                  2,
                                )}R`}
                          </p>

                        </div>

                      </div>


                      <div className="mt-4 flex flex-wrap gap-2 text-xs">

                        {trade.emotion && (
                          <span className="rounded-full border border-white/10 px-3 py-1 text-slate-400">
                            Psychology:{" "}
                            {trade.emotion}
                          </span>
                        )}

                        {trade.broker && (
                          <span className="rounded-full border border-white/10 px-3 py-1 text-slate-400">
                            Broker:{" "}
                            {trade.broker}
                          </span>
                        )}

                      </div>


                      {trade.notes && (
                        <div className="mt-4 rounded-2xl border border-white/[0.06] bg-black/20 p-4">

                          <p className="text-xs uppercase tracking-wider text-slate-500">
                            Journal Notes
                          </p>

                          <p className="mt-2 text-sm leading-6 text-slate-300">
                            {trade.notes}
                          </p>

                        </div>
                      )}

                    </article>
                  )
                },
              )
            ) : (
              <div className="rounded-2xl border border-dashed border-white/10 p-8 text-center text-sm text-slate-500">
                No trades found for this day.
              </div>
            )}

          </div>

        </div>


        <div className="mt-8 rounded-3xl border border-blue-400/10 bg-blue-400/[0.04] p-5">

          <div className="flex items-center gap-2">

            <Clock3 className="size-5 text-blue-300" />

            <p className="font-semibold">
              Daily intelligence
            </p>

          </div>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            TradePilot AI will use this daily history for
            discipline analysis, session performance,
            psychology patterns and future AI coaching.
          </p>

        </div>

      </aside>

    </div>
  )
}


export default function TradingCalendarPage() {
  const now =
    new Date()

  const [
    month,
    setMonth,
  ] = useState(
    new Date(
      now.getFullYear(),
      now.getMonth(),
      1,
    ),
  )

  const [
    selectedDate,
    setSelectedDate,
  ] = useState<
    string | null
  >(
    null,
  )


  const calendarQuery =
    useQuery({
      queryKey: [
        "trading-calendar",
      ],

      queryFn:
        fetchTradingCalendar,
    })


  const tradesQuery =
    useQuery({
      queryKey: [
        "calendar-trades",
      ],

      queryFn:
        fetchTrades,
    })


  const trades =
    tradesQuery.data
      ?.trades ||
    []


  const dayMap =
    useMemo(
      () => {
        const map =
          new Map()

        for (
          const day
          of calendarQuery.data
            ?.days ||
          []
        ) {
          map.set(
            day.date,
            day,
          )
        }

        return map
      },
      [
        calendarQuery.data,
      ],
    )


  const tradesByDate =
    useMemo(
      () => {
        const map =
          new Map<
            string,
            Trade[]
          >()

        for (
          const trade
          of trades
        ) {
          const date =
            getTradeDate(
              trade,
            )

          if (!date) {
            continue
          }

          const existing =
            map.get(
              date,
            ) ||
            []

          existing.push(
            trade,
          )

          map.set(
            date,
            existing,
          )
        }

        return map
      },
      [
        trades,
      ],
    )


  const year =
    month.getFullYear()

  const monthIndex =
    month.getMonth()

  const firstDay =
    new Date(
      year,
      monthIndex,
      1,
    )

  const lastDay =
    new Date(
      year,
      monthIndex + 1,
      0,
    )

  const startOffset =
    (
      firstDay.getDay() +
      6
    ) %
    7

  const totalDays =
    lastDay.getDate()

  const cells =
    Array.from({
      length:
        startOffset +
        totalDays,
    })


  const monthDays =
    calendarQuery.data
      ?.days.filter(
        (day) => {
          const date =
            new Date(
              `${day.date}T00:00:00`,
            )

          return (
            date.getFullYear() ===
              year &&
            date.getMonth() ===
              monthIndex
          )
        },
      ) ||
    []


  const monthProfit =
    monthDays.reduce(
      (
        total,
        day,
      ) =>
        total +
        day.net_profit,
      0,
    )


  const monthTrades =
    monthDays.reduce(
      (
        total,
        day,
      ) =>
        total +
        day.trades,
      0,
    )


  const profitableDays =
    monthDays.filter(
      (day) =>
        day.net_profit >
        0,
    ).length


  return (
    <div className="space-y-6">

      <section className="premium-card grid-surface rounded-[2rem] p-6 sm:p-8">

        <div className="flex items-center gap-3">

          <div className="grid size-11 place-items-center rounded-2xl bg-blue-400/10 text-blue-300">
            <CalendarDays className="size-5" />
          </div>

          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-blue-300">
            Trading Intelligence
          </p>

        </div>


        <h1 className="mt-5 text-3xl font-semibold sm:text-4xl">
          Trading Calendar
        </h1>


        <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
          Review every trading day, identify profitable patterns
          and inspect the trades behind each result.
        </p>

      </section>


      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <div className="premium-card rounded-3xl p-5">

          <p className="text-sm text-slate-500">
            Monthly P&L
          </p>

          <p
            className={[
              "mt-2 text-3xl font-semibold",

              monthProfit >= 0
                ? "text-emerald-300"
                : "text-red-300",

            ].join(" ")}
          >
            {money(
              monthProfit,
            )}
          </p>

        </div>


        <div className="premium-card rounded-3xl p-5">

          <p className="text-sm text-slate-500">
            Trading Days
          </p>

          <p className="mt-2 text-3xl font-semibold">
            {monthDays.length}
          </p>

        </div>


        <div className="premium-card rounded-3xl p-5">

          <p className="text-sm text-slate-500">
            Trades
          </p>

          <p className="mt-2 text-3xl font-semibold">
            {monthTrades}
          </p>

        </div>


        <div className="premium-card rounded-3xl p-5">

          <p className="text-sm text-slate-500">
            Profitable Days
          </p>

          <p className="mt-2 text-3xl font-semibold text-emerald-300">
            {profitableDays}
          </p>

        </div>

      </section>


      <section className="premium-card rounded-[2rem] p-4 sm:p-6">

        <div className="flex items-center justify-between">

          <button
            type="button"
            onClick={() =>
              setMonth(
                new Date(
                  year,
                  monthIndex -
                    1,
                  1,
                ),
              )
            }
            className="grid size-10 place-items-center rounded-2xl border border-white/10 bg-white/[0.03]"
          >
            <ChevronLeft className="size-5" />
          </button>


          <h2 className="text-lg font-semibold sm:text-xl">
            {month.toLocaleDateString(
              undefined,
              {
                month:
                  "long",

                year:
                  "numeric",
              },
            )}
          </h2>


          <button
            type="button"
            onClick={() =>
              setMonth(
                new Date(
                  year,
                  monthIndex +
                    1,
                  1,
                ),
              )
            }
            className="grid size-10 place-items-center rounded-2xl border border-white/10 bg-white/[0.03]"
          >
            <ChevronRight className="size-5" />
          </button>

        </div>


        <div className="mt-6 overflow-x-auto">

          <div className="min-w-[700px]">

            <div className="grid grid-cols-7 gap-2">

              {[
                "Mon",
                "Tue",
                "Wed",
                "Thu",
                "Fri",
                "Sat",
                "Sun",
              ].map(
                (
                  label,
                ) => (
                  <div
                    key={
                      label
                    }
                    className="py-2 text-center text-xs font-semibold uppercase text-slate-500"
                  >
                    {label}
                  </div>
                ),
              )}


              {cells.map(
                (
                  _,
                  index,
                ) => {
                  if (
                    index <
                    startOffset
                  ) {
                    return (
                      <div
                        key={`blank-${index}`}
                        className="min-h-28"
                      />
                    )
                  }


                  const dayNumber =
                    index -
                    startOffset +
                    1


                  const date =
                    `${year}-${String(
                      monthIndex +
                        1,
                    ).padStart(
                      2,
                      "0",
                    )}-${String(
                      dayNumber,
                    ).padStart(
                      2,
                      "0",
                    )}`


                  const stats =
                    dayMap.get(
                      date,
                    )


                  return (
                    <button
                      type="button"
                      key={
                        date
                      }
                      onClick={() => {
                        if (
                          stats
                        ) {
                          setSelectedDate(
                            date,
                          )
                        }
                      }}
                      className={[
                        "min-h-28 rounded-2xl border p-3 text-left transition",

                        stats
                          ? "cursor-pointer hover:-translate-y-1 hover:border-blue-400/30"

                          : "cursor-default",

                        stats
                          ?.result ===
                        "profit"
                          ? "border-emerald-400/20 bg-emerald-400/[0.06]"

                          : stats
                              ?.result ===
                            "loss"
                          ? "border-red-400/20 bg-red-400/[0.06]"

                          : stats
                          ? "border-slate-400/15 bg-white/[0.03]"

                          : "border-white/[0.06] bg-white/[0.015]",

                      ].join(
                        " ",
                      )}
                    >

                      <p className="text-sm font-semibold">
                        {dayNumber}
                      </p>


                      {stats && (
                        <div className="mt-4 space-y-1">

                          <p
                            className={[
                              "text-sm font-semibold",

                              stats.net_profit >=
                              0
                                ? "text-emerald-300"
                                : "text-red-300",

                            ].join(
                              " ",
                            )}
                          >
                            {money(
                              stats.net_profit,
                            )}
                          </p>


                          <p className="text-xs text-slate-500">
                            {stats.trades}{" "}
                            {stats.trades ===
                            1
                              ? "trade"
                              : "trades"}
                          </p>


                          <p className="text-xs text-slate-600">
                            {stats.win_rate.toFixed(
                              0,
                            )}
                            % win rate
                          </p>

                        </div>
                      )}

                    </button>
                  )
                },
              )}

            </div>

          </div>

        </div>

      </section>


      {selectedDate && (
        <DailyTradePanel
          date={
            selectedDate
          }
          trades={
            tradesByDate.get(
              selectedDate,
            ) ||
            []
          }
          onClose={() =>
            setSelectedDate(
              null,
            )
          }
        />
      )}

    </div>
  )
}
