import {
  CheckCircle2,
  Loader2,
  TrendingDown,
  TrendingUp,
  X,
} from "lucide-react"

import {
  useState,
} from "react"

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  closePaperTrade,
  getPaperTrades,
} from "@/api/aiSignals"


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
    trades.filter(
      trade =>
        trade.status ===
        "open",
    )


  const closedTrades =
    trades.filter(
      trade =>
        trade.status ===
        "closed",
    )


  const totalPL =
    closedTrades.reduce(
      (
        total,
        trade,
      ) =>
        total +
        (
          trade
            .profit_loss ??
          0
        ),

      0,
    )


  return (
    <div className="space-y-6">

      <header>

        <p className="text-xs uppercase tracking-[.25em] text-blue-300">
          Paper Trading
        </p>

        <h1 className="mt-3 text-3xl font-semibold">
          Test Signals Without Real Money
        </h1>

        <p className="mt-3 max-w-3xl text-slate-400">
          Track simulated trades generated
          from TradePilot AI signals before
          considering live execution.
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


      <section className="grid gap-4 md:grid-cols-3">

        <div className="premium-card rounded-3xl p-5">

          <p className="text-sm text-slate-500">
            Open Trades
          </p>

          <p className="mt-3 text-3xl font-semibold">
            {
              openTrades.length
            }
          </p>

        </div>


        <div className="premium-card rounded-3xl p-5">

          <p className="text-sm text-slate-500">
            Closed Trades
          </p>

          <p className="mt-3 text-3xl font-semibold">
            {
              closedTrades.length
            }
          </p>

        </div>


        <div className="premium-card rounded-3xl p-5">

          <p className="text-sm text-slate-500">
            Simulated P/L
          </p>

          <p
            className={[
              "mt-3 text-3xl font-semibold",

              totalPL >= 0
                ? "text-emerald-300"
                : "text-red-300",

            ].join(" ")}
          >
            {
              totalPL.toFixed(
                2,
              )
            }
          </p>

        </div>

      </section>


      <section className="premium-card rounded-3xl p-6">

        <h2 className="text-xl font-semibold">
          Open Paper Trades
        </h2>


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
                key={
                  trade.id
                }
                className="rounded-2xl bg-white/[.03] p-5"
              >

                <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">

                  <div>

                    <div className="flex items-center gap-3">

                      {trade.direction ===
                      "BUY"
                        ? (
                          <TrendingUp className="size-5 text-emerald-300"/>
                        )
                        : (
                          <TrendingDown className="size-5 text-red-300"/>
                        )}

                      <span className="text-lg font-semibold">
                        {
                          trade.symbol
                        }
                      </span>

                      <span
                        className={
                          trade.direction ===
                          "BUY"
                            ? "text-emerald-300"
                            : "text-red-300"
                        }
                      >
                        {
                          trade.direction
                        }
                      </span>

                    </div>


                    <div className="mt-3 flex flex-wrap gap-5 text-sm text-slate-400">

                      <span>
                        Entry:{" "}
                        {
                          trade.entry_price
                        }
                      </span>

                      <span>
                        SL:{" "}
                        {
                          trade.stop_loss ??
                          "—"
                        }
                      </span>

                      <span>
                        TP:{" "}
                        {
                          trade.take_profit ??
                          "—"
                        }
                      </span>

                      <span>
                        Risk:{" "}
                        {
                          trade.risk_percent
                        }%
                      </span>

                    </div>

                  </div>


                  <div className="flex flex-wrap gap-2">

                    <input
                      type="number"
                      step="any"
                      value={
                        exitPrices[
                          trade.id
                        ] ??
                        ""
                      }
                      onChange={(
                        event,
                      ) =>
                        setExitPrices(
                          previous => ({
                            ...previous,

                            [
                              trade.id
                            ]:
                              event
                                .target
                                .value,
                          }),
                        )
                      }
                      placeholder="Exit price"
                      className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-2"
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
                      className="flex items-center gap-2 rounded-2xl bg-blue-500 px-4 py-2 text-sm font-semibold disabled:opacity-50"
                    >

                      <X className="size-4"/>

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
            <p className="text-sm text-slate-500">
              No open paper trades.
            </p>
          )}

        </div>

      </section>


      <section className="premium-card rounded-3xl p-6">

        <h2 className="text-xl font-semibold">
          Closed Paper Trades
        </h2>


        <div className="mt-5 space-y-3">

          {closedTrades.map(
            trade => (
              <div
                key={
                  trade.id
                }
                className="flex flex-col justify-between gap-4 rounded-2xl bg-white/[.03] p-4 md:flex-row md:items-center"
              >

                <div className="flex items-center gap-3">

                  <CheckCircle2 className="size-4 text-blue-300"/>

                  <div>

                    <p className="font-semibold">
                      {
                        trade.symbol
                      }{" "}
                      {
                        trade.direction
                      }
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {
                        trade.entry_price
                      }{" "}
                      →{" "}
                      {
                        trade.exit_price
                      }
                    </p>

                  </div>

                </div>


                <p
                  className={
                    (
                      trade
                        .profit_loss ??
                      0
                    ) >= 0
                      ? "font-semibold text-emerald-300"
                      : "font-semibold text-red-300"
                  }
                >
                  {
                    (
                      trade
                        .profit_loss ??
                      0
                    ).toFixed(
                      2,
                    )
                  }
                </p>

              </div>
            ),
          )}


          {closedTrades.length ===
            0 && (
            <p className="text-sm text-slate-500">
              No completed paper trades yet.
            </p>
          )}

        </div>

      </section>

    </div>
  )
}
