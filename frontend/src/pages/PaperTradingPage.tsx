import {
  CheckCircle2,
  Clock3,
  Loader2,
  Minus,
  TrendingDown,
  TrendingUp,
  Trophy,
  X,
} from "lucide-react"

import {
  useMemo,
  useState,
} from "react"

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  closePaperTrade,
  getPaperTradeAnalytics,
  getPaperTrades,
  type PaperTrade,
  type PaperTradeAnalytics,
} from "@/api/aiSignals"


function formatDuration(
  minutes:
    | number
    | null
    | undefined,
) {
  if (
    minutes === null ||
    minutes === undefined
  ) {
    return "—"
  }

  if (minutes < 60) {
    return `${minutes} min`
  }

  const hours =
    Math.floor(
      minutes / 60,
    )

  const remaining =
    minutes % 60

  return remaining
    ? `${hours}h ${remaining}m`
    : `${hours}h`
}


function formatR(
  value:
    | number
    | null
    | undefined,
) {
  if (
    value === null ||
    value === undefined
  ) {
    return "—"
  }

  const formatted =
    value.toFixed(2)

  return value > 0
    ? `+${formatted}R`
    : `${formatted}R`
}


function resultClass(
  trade: PaperTrade,
) {
  if (trade.result === "WIN") {
    return "text-emerald-300"
  }

  if (trade.result === "LOSS") {
    return "text-red-300"
  }

  return "text-amber-300"
}


export default function PaperTradingPage() {
  const qc =
    useQueryClient()

  const [
    exitPrices,
    setExitPrices,
  ] = useState<
    Record<number, string>
  >({})

  const [
    message,
    setMessage,
  ] = useState("")

  const [
    error,
    setError,
  ] = useState("")


  const tradesQuery =
    useQuery({
      queryKey: [
        "paper-trades",
      ],

      queryFn:
        getPaperTrades,
    })


  const analyticsQuery =
    useQuery<PaperTradeAnalytics>({
      queryKey: [
        "paper-trade-analytics",
      ],

      queryFn:
        getPaperTradeAnalytics,
    })


  const closeMutation =
    useMutation({
      mutationFn:
        ({
          tradeId,
          exitPrice,
        }: {
          tradeId: number
          exitPrice: number
        }) =>
          closePaperTrade(
            tradeId,
            exitPrice,
          ),

      onMutate: () => {
        setMessage("")
        setError("")
      },

      onSuccess:
        async () => {
          setMessage(
            "Paper trade closed.",
          )

          await qc
            .invalidateQueries({
              queryKey: [
                "paper-trades",
              ],
            })

          await qc
            .invalidateQueries({
              queryKey: [
                "paper-trade-analytics",
              ],
            })
        },

      onError: (
        mutationError:
          any,
      ) => {
        const detail =
          mutationError
            ?.response
            ?.data
            ?.detail

        setError(
          typeof detail ===
            "string"
            ? detail
            : "Unable to close paper trade.",
        )
      },
    })


  function closeTrade(
    tradeId: number,
  ) {
    const price =
      Number(
        exitPrices[
          tradeId
        ],
      )

    if (
      !Number.isFinite(
        price,
      ) ||
      price <= 0
    ) {
      setError(
        "Enter a valid exit price.",
      )

      return
    }

    closeMutation.mutate({
      tradeId,
      exitPrice:
        price,
    })
  }


  const trades =
    tradesQuery
      .data
      ?.trades ??
    []


  const openTrades =
    useMemo(
      () =>
        trades.filter(
          trade =>
            trade.status ===
            "open",
        ),
      [trades],
    )


  const closedTrades =
    useMemo(
      () =>
        trades.filter(
          trade =>
            trade.status ===
            "closed",
        ),
      [trades],
    )


  const metrics =
    useMemo(
      () => {
        const wins =
          closedTrades.filter(
            trade =>
              trade.result ===
              "WIN",
          )

        const losses =
          closedTrades.filter(
            trade =>
              trade.result ===
              "LOSS",
          )

        const breakeven =
          closedTrades.filter(
            trade =>
              trade.result ===
              "BREAKEVEN",
          )

        const tradesWithR =
          closedTrades.filter(
            trade =>
              typeof
                trade.r_multiple ===
              "number",
          )

        const totalR =
          tradesWithR.reduce(
            (
              total,
              trade,
            ) =>
              total +
              (
                trade.r_multiple ??
                0
              ),
            0,
          )

        const averageR =
          tradesWithR.length
            ? totalR /
              tradesWithR.length
            : 0

        const winRate =
          closedTrades.length
            ? (
                wins.length /
                closedTrades.length
              ) *
              100
            : 0

        const best =
          tradesWithR.length
            ? Math.max(
                ...tradesWithR.map(
                  trade =>
                    trade.r_multiple ??
                    0,
                ),
              )
            : null

        const worst =
          tradesWithR.length
            ? Math.min(
                ...tradesWithR.map(
                  trade =>
                    trade.r_multiple ??
                    0,
                ),
              )
            : null

        return {
          wins:
            wins.length,

          losses:
            losses.length,

          breakeven:
            breakeven.length,

          totalR,

          averageR,

          winRate,

          best,

          worst,
        }
      },
      [closedTrades],
    )


  return (
    <div className="space-y-6">

      <header>

        <p className="text-xs uppercase tracking-[.25em] text-blue-300">
          Paper Trading
        </p>

        <h1 className="mt-3 text-3xl font-semibold">
          Performance Lab
        </h1>

        <p className="mt-3 max-w-3xl text-slate-400">
          Track simulated AI trades,
          measure strategy quality and
          learn from outcomes before
          risking real capital.
        </p>

      </header>


      {message && (
        <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/[.07] p-4 text-emerald-300">
          {message}
        </div>
      )}


      {error && (
        <div className="rounded-2xl border border-red-400/20 bg-red-400/[.07] p-4 text-red-300">
          {error}
        </div>
      )}


      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">

        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Total Trades
          </p>

          <p className="mt-3 text-3xl font-semibold">
            {trades.length}
          </p>
        </div>


        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Open Positions
          </p>

          <p className="mt-3 text-3xl font-semibold">
            {openTrades.length}
          </p>
        </div>


        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Win Rate
          </p>

          <p className="mt-3 text-3xl font-semibold text-emerald-300">
            {metrics.winRate.toFixed(
              1,
            )}%
          </p>
        </div>


        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Total R
          </p>

          <p
            className={[
              "mt-3 text-3xl font-semibold",

              metrics.totalR >= 0
                ? "text-emerald-300"
                : "text-red-300",

            ].join(" ")}
          >
            {formatR(
              metrics.totalR,
            )}
          </p>
        </div>


        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Average R
          </p>

          <p
            className={[
              "mt-3 text-3xl font-semibold",

              metrics.averageR >= 0
                ? "text-emerald-300"
                : "text-red-300",

            ].join(" ")}
          >
            {formatR(
              metrics.averageR,
            )}
          </p>
        </div>

      </section>


      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">

        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Wins
          </p>

          <p className="mt-3 text-2xl font-semibold text-emerald-300">
            {metrics.wins}
          </p>
        </div>


        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Losses
          </p>

          <p className="mt-3 text-2xl font-semibold text-red-300">
            {metrics.losses}
          </p>
        </div>


        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Breakeven
          </p>

          <p className="mt-3 text-2xl font-semibold text-amber-300">
            {metrics.breakeven}
          </p>
        </div>


        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Best Trade
          </p>

          <p className="mt-3 text-2xl font-semibold text-emerald-300">
            {formatR(
              metrics.best,
            )}
          </p>
        </div>


        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Worst Trade
          </p>

          <p className="mt-3 text-2xl font-semibold text-red-300">
            {formatR(
              metrics.worst,
            )}
          </p>
        </div>

      </section>


      <section className="space-y-5">

        <div>
          <p className="text-xs uppercase tracking-[.25em] text-blue-300">
            Strategy Intelligence
          </p>

          <h2 className="mt-2 text-2xl font-semibold">
            Performance Analytics
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Performance is calculated from closed paper trades linked back to the AI signal and strategy that generated them.
          </p>
        </div>


        {analyticsQuery.isLoading ? (
          <div className="premium-card flex items-center gap-3 rounded-3xl p-6 text-slate-400">
            <Loader2 className="size-5 animate-spin"/>
            Loading strategy analytics...
          </div>
        ) : analyticsQuery.isError ? (
          <div className="premium-card rounded-3xl p-6 text-red-300">
            Unable to load strategy analytics.
          </div>
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

              <div className="premium-card rounded-3xl p-5">
                <p className="text-sm text-slate-500">
                  Backend Win Rate
                </p>

                <p className="mt-3 text-3xl font-semibold text-emerald-300">
                  {(analyticsQuery.data?.summary.win_rate ?? 0).toFixed(1)}%
                </p>
              </div>


              <div className="premium-card rounded-3xl p-5">
                <p className="text-sm text-slate-500">
                  Backend Total R
                </p>

                <p className="mt-3 text-3xl font-semibold">
                  {formatR(
                    analyticsQuery.data?.summary.total_r ?? 0,
                  )}
                </p>
              </div>


              <div className="premium-card rounded-3xl p-5">
                <p className="text-sm text-slate-500">
                  Average R
                </p>

                <p className="mt-3 text-3xl font-semibold">
                  {formatR(
                    analyticsQuery.data?.summary.average_r ?? 0,
                  )}
                </p>
              </div>


              <div className="premium-card rounded-3xl p-5">
                <p className="text-sm text-slate-500">
                  Average Duration
                </p>

                <p className="mt-3 text-3xl font-semibold">
                  {formatDuration(
                    analyticsQuery.data?.summary
                      .average_duration_minutes ?? 0,
                  )}
                </p>
              </div>

            </div>


            <div className="grid gap-5 xl:grid-cols-2">

              <div className="premium-card rounded-[2rem] p-5 sm:p-6">

                <h3 className="text-xl font-semibold">
                  Strategy Leaderboard
                </h3>

                <div className="mt-5 space-y-3">

                  {analyticsQuery.data?.strategies.length ? (
                    analyticsQuery.data.strategies.map(
                      (strategy, index) => (
                        <div
                          key={`${strategy.strategy_id}-${strategy.strategy_name}`}
                          className="rounded-2xl border border-white/[.06] bg-white/[.025] p-4"
                        >

                          <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">

                            <div>
                              <p className="text-xs text-slate-500">
                                #{index + 1}
                              </p>

                              <p className="mt-1 font-semibold">
                                {strategy.strategy_name}
                              </p>
                            </div>

                            <p
                              className={[
                                "text-xl font-semibold",

                                strategy.total_r >= 0
                                  ? "text-emerald-300"
                                  : "text-red-300",

                              ].join(" ")}
                            >
                              {formatR(
                                strategy.total_r,
                              )}
                            </p>

                          </div>


                          <div className="mt-4 grid grid-cols-3 gap-3 text-sm">

                            <div>
                              <p className="text-xs text-slate-500">
                                Trades
                              </p>
                              <p className="mt-1 font-semibold">
                                {strategy.trades}
                              </p>
                            </div>

                            <div>
                              <p className="text-xs text-slate-500">
                                Win Rate
                              </p>
                              <p className="mt-1 font-semibold">
                                {strategy.win_rate.toFixed(1)}%
                              </p>
                            </div>

                            <div>
                              <p className="text-xs text-slate-500">
                                Avg R
                              </p>
                              <p className="mt-1 font-semibold">
                                {formatR(strategy.average_r)}
                              </p>
                            </div>

                          </div>

                        </div>
                      ),
                    )
                  ) : (
                    <p className="rounded-2xl border border-dashed border-white/10 p-6 text-sm text-slate-500">
                      Close paper trades to build your strategy leaderboard.
                    </p>
                  )}

                </div>

              </div>


              <div className="premium-card rounded-[2rem] p-5 sm:p-6">

                <h3 className="text-xl font-semibold">
                  Symbol Performance
                </h3>

                <div className="mt-5 space-y-3">

                  {analyticsQuery.data?.symbols.length ? (
                    analyticsQuery.data.symbols.map(
                      item => (
                        <div
                          key={item.symbol}
                          className="flex items-center justify-between gap-4 rounded-2xl border border-white/[.06] bg-white/[.025] p-4"
                        >

                          <div>
                            <p className="font-semibold">
                              {item.symbol}
                            </p>

                            <p className="mt-1 text-xs text-slate-500">
                              {item.trades} trades - {item.win_rate.toFixed(1)}% win rate
                            </p>
                          </div>

                          <p
                            className={[
                              "font-semibold",

                              item.total_r >= 0
                                ? "text-emerald-300"
                                : "text-red-300",

                            ].join(" ")}
                          >
                            {formatR(item.total_r)}
                          </p>

                        </div>
                      ),
                    )
                  ) : (
                    <p className="rounded-2xl border border-dashed border-white/10 p-6 text-sm text-slate-500">
                      No symbol performance data yet.
                    </p>
                  )}

                </div>

              </div>

            </div>


            <div className="grid gap-5 xl:grid-cols-2">

              <div className="premium-card rounded-[2rem] p-5 sm:p-6">

                <h3 className="text-xl font-semibold">
                  Timeframe Performance
                </h3>

                <div className="mt-5 space-y-3">

                  {analyticsQuery.data?.timeframes.length ? (
                    analyticsQuery.data.timeframes.map(
                      item => (
                        <div
                          key={item.timeframe}
                          className="flex items-center justify-between rounded-2xl bg-white/[.025] p-4"
                        >

                          <div>
                            <p className="font-semibold">
                              {item.timeframe}
                            </p>

                            <p className="mt-1 text-xs text-slate-500">
                              {item.trades} trades
                            </p>
                          </div>

                          <div className="text-right">
                            <p className="font-semibold">
                              {item.win_rate.toFixed(1)}%
                            </p>

                            <p className="mt-1 text-xs text-slate-500">
                              {formatR(item.total_r)}
                            </p>
                          </div>

                        </div>
                      ),
                    )
                  ) : (
                    <p className="text-sm text-slate-500">
                      No timeframe data yet.
                    </p>
                  )}

                </div>

              </div>


              <div className="premium-card rounded-[2rem] p-5 sm:p-6">

                <h3 className="text-xl font-semibold">
                  Confidence Performance
                </h3>

                <p className="mt-2 text-sm text-slate-400">
                  See whether higher AI confidence actually produces better outcomes.
                </p>

                <div className="mt-5 space-y-3">

                  {analyticsQuery.data?.confidence_bands.length ? (
                    analyticsQuery.data.confidence_bands.map(
                      item => (
                        <div
                          key={item.band}
                          className="rounded-2xl bg-white/[.025] p-4"
                        >

                          <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">

                            <p className="font-semibold">
                              {item.band}% confidence
                            </p>

                            <p className="font-semibold text-blue-300">
                              {item.win_rate.toFixed(1)}%
                            </p>

                          </div>

                          <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/[.05]">
                            <div
                              className="h-full rounded-full bg-blue-400"
                              style={{
                                width: `${Math.min(
                                  100,
                                  Math.max(
                                    0,
                                    item.win_rate,
                                  ),
                                )}%`,
                              }}
                            />
                          </div>

                          <div className="mt-3 flex justify-between text-xs text-slate-500">
                            <span>
                              {item.trades} trades
                            </span>

                            <span>
                              {formatR(item.total_r)}
                            </span>
                          </div>

                        </div>
                      ),
                    )
                  ) : (
                    <p className="text-sm text-slate-500">
                      No confidence-band data yet.
                    </p>
                  )}

                </div>

              </div>

            </div>
          </>
        )}

      </section>


      <section className="premium-card rounded-[2rem] p-5 sm:p-6">

        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">

          <div>
            <p className="text-xs uppercase tracking-[.2em] text-blue-300">
              Live Simulation
            </p>

            <h2 className="mt-2 text-xl font-semibold">
              Open Paper Trades
            </h2>
          </div>

          <span className="rounded-full border border-white/10 bg-white/[.03] px-3 py-1 text-xs text-slate-400">
            {openTrades.length} open
          </span>

        </div>


        <div className="mt-5 space-y-4">

          {tradesQuery
            .isLoading && (
            <div className="flex items-center gap-2 text-slate-400">

              <Loader2 className="size-4 animate-spin"/>

              Loading trades...

            </div>
          )}


          {openTrades.map(
            trade => (
              <article
                key={trade.id}
                className="rounded-3xl border border-white/[.06] bg-white/[.025] p-5"
              >

                <div className="flex flex-col justify-between gap-5 xl:flex-row xl:items-center">

                  <div>

                    <div className="flex flex-wrap items-center gap-3">

                      {trade.direction ===
                      "BUY"
                        ? (
                          <TrendingUp className="size-5 text-emerald-300"/>
                        )
                        : (
                          <TrendingDown className="size-5 text-red-300"/>
                        )}

                      <span className="text-lg font-semibold">
                        {trade.symbol}
                      </span>

                      <span
                        className={[
                          "rounded-full px-3 py-1 text-xs font-semibold",

                          trade.direction ===
                          "BUY"
                            ? "bg-emerald-400/[.08] text-emerald-300"
                            : "bg-red-400/[.08] text-red-300",

                        ].join(" ")}
                      >
                        {trade.direction}
                      </span>

                      <span className="rounded-full bg-blue-400/[.08] px-3 py-1 text-xs text-blue-300">
                        OPEN
                      </span>

                    </div>


                    <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">

                      <div>
                        <p className="text-xs text-slate-500">
                          Entry
                        </p>

                        <p className="mt-1 font-semibold">
                          {trade.entry_price}
                        </p>
                      </div>


                      <div>
                        <p className="text-xs text-slate-500">
                          Stop Loss
                        </p>

                        <p className="mt-1 font-semibold text-red-300">
                          {trade.stop_loss ??
                            "—"}
                        </p>
                      </div>


                      <div>
                        <p className="text-xs text-slate-500">
                          Take Profit
                        </p>

                        <p className="mt-1 font-semibold text-emerald-300">
                          {trade.take_profit ??
                            "—"}
                        </p>
                      </div>


                      <div>
                        <p className="text-xs text-slate-500">
                          Risk
                        </p>

                        <p className="mt-1 font-semibold">
                          {trade.risk_percent}%
                        </p>
                      </div>

                    </div>

                  </div>


                  <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:flex-wrap">

                    <input
                      type="number"
                      step="any"
                      value={
                        exitPrices[
                          trade.id
                        ] ??
                        ""
                      }
                      onChange={event =>
                        setExitPrices(
                          previous => ({
                            ...previous,

                            [trade.id]:
                              event.target.value,
                          }),
                        )
                      }
                      placeholder="Exit price"
                      className="w-full min-w-0 rounded-2xl border border-white/10 bg-white/[.03] px-4 py-2 outline-none sm:w-auto sm:min-w-[170px]"
                    />


                    <button
                      type="button"
                      disabled={
                        closeMutation
                          .isPending
                      }
                      onClick={() =>
                        closeTrade(
                          trade.id,
                        )
                      }
                      className="flex w-full items-center justify-center gap-2 rounded-2xl bg-blue-500 px-4 py-2 text-sm font-semibold disabled:opacity-50 sm:w-auto"
                    >

                      {closeMutation
                        .isPending
                        ? (
                          <Loader2 className="size-4 animate-spin"/>
                        )
                        : (
                          <X className="size-4"/>
                        )}

                      Close Trade

                    </button>

                  </div>

                </div>

              </article>
            ),
          )}


          {!tradesQuery
            .isLoading &&
            openTrades.length ===
              0 && (
            <div className="rounded-3xl border border-dashed border-white/10 p-5 text-center sm:p-8">

              <p className="text-sm text-slate-500">
                No open paper trades.
              </p>

              <p className="mt-2 text-xs text-slate-600">
                Send a qualified BUY or SELL signal from AI Signal Lab to start one.
              </p>

            </div>
          )}

        </div>

      </section>


      <section className="premium-card rounded-[2rem] p-5 sm:p-6">

        <div className="flex items-center gap-3">

          <Trophy className="size-5 text-amber-300"/>

          <div>
            <p className="text-xs uppercase tracking-[.2em] text-amber-300">
              Performance History
            </p>

            <h2 className="mt-1 text-xl font-semibold">
              Closed Paper Trades
            </h2>
          </div>

        </div>


        <div className="mt-5 space-y-3">

          {closedTrades.map(
            trade => (
              <div
                key={trade.id}
                className="rounded-3xl border border-white/[.06] bg-white/[.025] p-5"
              >

                <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">

                  <div className="flex min-w-0 items-start gap-3">

                    {trade.result ===
                    "WIN"
                      ? (
                        <CheckCircle2 className="mt-1 size-5 shrink-0 text-emerald-300"/>
                      )
                      : trade.result ===
                        "LOSS"
                      ? (
                        <TrendingDown className="mt-1 size-5 shrink-0 text-red-300"/>
                      )
                      : (
                        <Minus className="mt-1 size-5 shrink-0 text-amber-300"/>
                      )}

                    <div>

                      <div className="flex flex-wrap items-center gap-3">

                        <p className="font-semibold">
                          {trade.symbol}{" "}
                          {trade.direction}
                        </p>

                        <span
                          className={[
                            "rounded-full px-3 py-1 text-xs font-semibold",

                            trade.result ===
                            "WIN"
                              ? "bg-emerald-400/[.08] text-emerald-300"
                              : trade.result ===
                                "LOSS"
                              ? "bg-red-400/[.08] text-red-300"
                              : "bg-amber-400/[.08] text-amber-300",

                          ].join(" ")}
                        >
                          {trade.result ||
                            "CLOSED"}
                        </span>

                      </div>


                      <p className="mt-2 text-sm text-slate-500">
                        {trade.entry_price}
                        {" → "}
                        {trade.exit_price ??
                          "—"}
                      </p>


                      <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-500">

                        <span className="flex items-center gap-1">
                          <Clock3 className="size-3"/>

                          {formatDuration(
                            trade.duration_minutes,
                          )}
                        </span>

                        <span>
                          Risk:{" "}
                          {trade.risk_percent}%
                        </span>

                        <span>
                          Signal #{trade.signal_id}
                        </span>

                      </div>

                    </div>

                  </div>


                  <div className="flex w-full items-center justify-between gap-4 sm:w-auto sm:justify-start sm:gap-6">

                    <div className="text-right">
                      <p className="text-xs text-slate-500">
                        Price Move
                      </p>

                      <p
                        className={[
                          "mt-1 font-semibold",

                          (
                            trade.profit_loss ??
                            0
                          ) >= 0
                            ? "text-emerald-300"
                            : "text-red-300",

                        ].join(" ")}
                      >
                        {(
                          trade.profit_loss ??
                          0
                        ).toFixed(
                          2,
                        )}
                      </p>
                    </div>


                    <div className="text-right">
                      <p className="text-xs text-slate-500">
                        R-Multiple
                      </p>

                      <p
                        className={[
                          "mt-1 text-xl font-semibold",

                          resultClass(
                            trade,
                          ),

                        ].join(" ")}
                      >
                        {formatR(
                          trade.r_multiple,
                        )}
                      </p>
                    </div>

                  </div>

                </div>

              </div>
            ),
          )}


          {closedTrades.length ===
            0 && (
            <div className="rounded-3xl border border-dashed border-white/10 p-5 text-center sm:p-8">

              <p className="text-sm text-slate-500">
                No completed paper trades yet.
              </p>

              <p className="mt-2 text-xs text-slate-600">
                Close a simulated position to begin building performance statistics.
              </p>

            </div>
          )}

        </div>

      </section>

    </div>
  )
}
