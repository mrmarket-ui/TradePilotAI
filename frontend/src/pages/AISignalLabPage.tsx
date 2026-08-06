import {
  BrainCircuit,
  CheckCircle2,
  Image as ImageIcon,
  Loader2,
  ShieldCheck,
  XCircle,
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
  analyzeChart,
  getAISignals,
  paperTradeSignal,
  type AISignal,
} from "@/api/aiSignals"

import {
  getSavedStrategies,
} from "@/api/savedStrategies"


function formatNumber(
  value:
    | number
    | null
    | undefined,
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return "—"
  }

  return String(value)
}


export default function AISignalLabPage() {
  const queryClient =
    useQueryClient()

  const [
    strategyId,
    setStrategyId,
  ] = useState("")

  const [
    symbol,
    setSymbol,
  ] = useState(
    "XAUUSD",
  )

  const [
    timeframe,
    setTimeframe,
  ] = useState(
    "15M",
  )

  const [
    chart,
    setChart,
  ] = useState<File | null>(
    null,
  )

  const [
    entry,
    setEntry,
  ] = useState("")

  const [
    riskPercent,
    setRiskPercent,
  ] = useState(
    "0.5",
  )

  const [
    message,
    setMessage,
  ] = useState("")

  const [
    error,
    setError,
  ] = useState("")


  const strategiesQuery =
    useQuery({
      queryKey: [
        "strategies",
      ],

      queryFn:
        getSavedStrategies,
    })


  const signalsQuery =
    useQuery({
      queryKey: [
        "ai-signals",
      ],

      queryFn:
        getAISignals,
    })


  const analyzeMutation =
    useMutation({
      mutationFn:
        async () => {
          if (!chart) {
            throw new Error(
              "Choose a chart image.",
            )
          }

          if (!strategyId) {
            throw new Error(
              "Choose a trading strategy.",
            )
          }

          if (
            !symbol.trim()
          ) {
            throw new Error(
              "Enter a symbol.",
            )
          }

          if (
            !timeframe.trim()
          ) {
            throw new Error(
              "Enter a timeframe.",
            )
          }

          return analyzeChart({
            strategyId:
              Number(
                strategyId,
              ),

            symbol:
              symbol.trim(),

            timeframe:
              timeframe.trim(),

            chart,
          })
        },

      onMutate: () => {
        setMessage("")
        setError("")
      },

      onSuccess:
        async (
          result,
        ) => {
          setMessage(
            `Analysis complete: ${result.direction}`,
          )

          await queryClient
            .invalidateQueries({
              queryKey: [
                "ai-signals",
              ],
            })
        },

      onError: (
        mutationError:
          unknown,
      ) => {
        if (
          mutationError
          instanceof Error
        ) {
          setError(
            mutationError.message,
          )

          return
        }

        setError(
          "Chart analysis failed.",
        )
      },
    })


  const paperMutation =
    useMutation({
      mutationFn:
        async ({
          signalId,
          entryPrice,
          risk,
        }: {
          signalId: number
          entryPrice: number
          risk: number
        }) =>
          paperTradeSignal(
            signalId,
            entryPrice,
            risk,
          ),

      onMutate: () => {
        setMessage("")
        setError("")
      },

      onSuccess:
        async () => {
          setMessage(
            "Paper trade opened successfully.",
          )

          setEntry("")

          await queryClient
            .invalidateQueries({
              queryKey: [
                "ai-signals",
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

        if (
          typeof detail
          === "string"
        ) {
          setError(detail)

          return
        }

        setError(
          "Unable to open paper trade.",
        )
      },
    })


  const current:
    AISignal | undefined =
      analyzeMutation.data ??
      signalsQuery
        .data
        ?.signals
        ?.[0]


  function startPaperTrade() {
    if (!current) {
      return
    }

    const entryPrice =
      Number(entry)

    const risk =
      Number(
        riskPercent,
      )

    if (
      !Number.isFinite(
        entryPrice,
      ) ||
      entryPrice <= 0
    ) {
      setError(
        "Enter a valid paper entry price.",
      )

      return
    }

    if (
      !Number.isFinite(
        risk,
      ) ||
      risk <= 0
    ) {
      setError(
        "Enter a valid risk percentage.",
      )

      return
    }

    paperMutation.mutate({
      signalId:
        current.id,

      entryPrice,

      risk,
    })
  }


  return (
    <div className="space-y-6">

      <header>
        <p className="text-xs uppercase tracking-[.25em] text-blue-300">
          AI Signal Lab
        </p>

        <h1 className="mt-3 text-3xl font-semibold">
          Analyze Your Trading Setup
        </h1>

        <p className="mt-3 max-w-3xl leading-7 text-slate-400">
          Upload a chart screenshot.
          TradePilot AI compares the visible
          setup against your selected trading
          strategy and returns BUY, SELL or
          NO TRADE.
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


      <section className="premium-card rounded-3xl p-6">

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">

          <label>
            <span className="mb-2 block text-sm text-slate-400">
              Trading Strategy
            </span>

            <select
              value={
                strategyId
              }
              disabled={
                strategiesQuery
                  .isLoading
              }
              onChange={(
                event,
              ) =>
                setStrategyId(
                  event
                    .target
                    .value,
                )
              }
              className="w-full rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3 outline-none"
            >
              <option value="">
                {strategiesQuery
                  .isLoading
                  ? "Loading strategies..."
                  : "Select strategy"}
              </option>

              {strategiesQuery
                .data
                ?.strategies
                ?.map(
                  strategy => (
                    <option
                      key={
                        strategy.id
                      }
                      value={
                        strategy.id
                      }
                    >
                      {
                        strategy.name
                      }

                      {
                        strategy
                          .is_active
                          ? " — Active"
                          : ""
                      }
                    </option>
                  ),
                )}
            </select>
          </label>


          <label>
            <span className="mb-2 block text-sm text-slate-400">
              Symbol
            </span>

            <input
              value={
                symbol
              }
              onChange={(
                event,
              ) =>
                setSymbol(
                  event
                    .target
                    .value
                    .toUpperCase(),
                )
              }
              placeholder="XAUUSD"
              className="w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3 outline-none"
            />
          </label>


          <label>
            <span className="mb-2 block text-sm text-slate-400">
              Timeframe
            </span>

            <input
              value={
                timeframe
              }
              onChange={(
                event,
              ) =>
                setTimeframe(
                  event
                    .target
                    .value,
                )
              }
              placeholder="15M"
              className="w-full rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3 outline-none"
            />
          </label>


          <label>
            <span className="mb-2 block text-sm text-slate-400">
              Chart Screenshot
            </span>

            <div className="flex min-h-[50px] cursor-pointer items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3">

              <ImageIcon className="size-4 text-blue-300"/>

              <span className="truncate text-sm">
                {chart
                  ? chart.name
                  : "Choose chart"}
              </span>

              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                className="hidden"
                onChange={(
                  event,
                ) => {
                  const file =
                    event
                      .target
                      .files
                      ?.[0]

                  setChart(
                    file ??
                    null,
                  )
                }}
              />

            </div>
          </label>

        </div>


        <button
          type="button"
          disabled={
            !strategyId ||
            !symbol.trim() ||
            !timeframe.trim() ||
            !chart ||
            analyzeMutation
              .isPending
          }
          onClick={() =>
            analyzeMutation
              .mutate()
          }
          className="mt-6 flex items-center gap-2 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-3 font-semibold disabled:cursor-not-allowed disabled:opacity-50"
        >

          {analyzeMutation
            .isPending
            ? (
              <Loader2 className="size-4 animate-spin"/>
            )
            : (
              <BrainCircuit className="size-4"/>
            )}

          {analyzeMutation
            .isPending
            ? "Analyzing Chart..."
            : "Analyze Setup"}

        </button>

      </section>


      {current && (
        <section className="premium-card rounded-[2rem] p-7">

          <div className="flex flex-wrap items-center justify-between gap-6">

            <div>
              <p className="text-sm text-slate-500">
                AI Decision
              </p>

              <h2
                className={[
                  "mt-2 text-4xl font-bold",

                  current.direction ===
                  "BUY"
                    ? "text-emerald-300"
                    : current.direction ===
                      "SELL"
                    ? "text-red-300"
                    : "text-amber-300",

                ].join(" ")}
              >
                {
                  current.direction
                }
              </h2>
            </div>


            <div>
              <p className="text-sm text-slate-500">
                Symbol
              </p>

              <p className="mt-2 text-2xl font-semibold">
                {current.symbol}
              </p>
            </div>


            <div>
              <p className="text-sm text-slate-500">
                Confidence
              </p>

              <p className="mt-2 text-3xl font-semibold">
                {
                  current.confidence
                }%
              </p>
            </div>


            <div>
              <p className="text-sm text-slate-500">
                Setup Score
              </p>

              <p className="mt-2 text-3xl font-semibold">
                {
                  current.setup_score
                }/100
              </p>
            </div>

          </div>


          <div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">

            <div className="rounded-2xl bg-white/[.03] p-4">

              <p className="text-xs text-slate-500">
                Entry
              </p>

              <p className="mt-2 font-semibold">

                {
                  current.entry_low !=
                    null &&
                  current.entry_high !=
                    null
                    ? `${current.entry_low} – ${current.entry_high}`
                    : formatNumber(
                        current.entry_low ??
                        current.entry_high,
                      )
                }

              </p>

            </div>


            {[
              [
                "Stop Loss",
                current.stop_loss,
              ],

              [
                "TP1",
                current.take_profit_1,
              ],

              [
                "TP2",
                current.take_profit_2,
              ],

              [
                "TP3",
                current.take_profit_3,
              ],

              [
                "Risk / Reward",
                current.risk_reward,
              ],

            ].map(
              ([
                label,
                value,
              ]) => (
                <div
                  key={
                    String(
                      label,
                    )
                  }
                  className="rounded-2xl bg-white/[.03] p-4"
                >

                  <p className="text-xs text-slate-500">
                    {label}
                  </p>

                  <p className="mt-2 font-semibold">
                    {
                      formatNumber(
                        value as
                          | number
                          | null
                          | undefined,
                      )
                    }
                  </p>

                </div>
              ),
            )}

          </div>


          {current.reasoning && (
            <div className="mt-6 rounded-2xl border border-blue-400/10 bg-blue-400/[.04] p-5">

              <p className="font-semibold text-blue-300">
                AI Reasoning
              </p>

              <p className="mt-3 leading-7 text-slate-300">
                {
                  current.reasoning
                }
              </p>

            </div>
          )}


          {current
            .matched_rules
            ?.length >
            0 && (
            <div className="mt-6">

              <p className="font-semibold text-emerald-300">
                Matched Strategy Rules
              </p>

              <div className="mt-3 space-y-2">

                {
                  current
                    .matched_rules
                    .map(
                      rule => (
                        <div
                          key={
                            rule
                          }
                          className="flex gap-3 rounded-2xl bg-emerald-400/[.05] p-3 text-sm"
                        >

                          <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-300"/>

                          <span>
                            {rule}
                          </span>

                        </div>
                      ),
                    )
                }

              </div>

            </div>
          )}


          {current
            .missing_rules
            ?.length >
            0 && (
            <div className="mt-6">

              <p className="font-semibold text-red-300">
                Missing Confirmations
              </p>

              <div className="mt-3 space-y-2">

                {
                  current
                    .missing_rules
                    .map(
                      rule => (
                        <div
                          key={
                            rule
                          }
                          className="flex gap-3 rounded-2xl bg-red-400/[.05] p-3 text-sm"
                        >

                          <XCircle className="mt-0.5 size-4 shrink-0 text-red-300"/>

                          <span>
                            {rule}
                          </span>

                        </div>
                      ),
                    )
                }

              </div>

            </div>
          )}


          {current.invalidation && (
            <div className="mt-6 rounded-2xl bg-amber-400/[.05] p-5">

              <p className="font-semibold text-amber-300">
                Setup Invalidation
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-300">
                {
                  current
                    .invalidation
                }
              </p>

            </div>
          )}


          {current.direction !==
            "NO_TRADE" && (
            <div className="mt-7 border-t border-white/10 pt-6">

              <h3 className="text-xl font-semibold">
                Paper Trade Simulator
              </h3>

              <p className="mt-2 text-sm text-slate-400">
                Test the setup without risking real money.
              </p>


              <div className="mt-5 flex flex-wrap gap-3">

                <input
                  value={
                    entry
                  }
                  onChange={(
                    event,
                  ) =>
                    setEntry(
                      event
                        .target
                        .value,
                    )
                  }
                  type="number"
                  step="any"
                  placeholder="Entry price"
                  className="rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3 outline-none"
                />


                <input
                  value={
                    riskPercent
                  }
                  onChange={(
                    event,
                  ) =>
                    setRiskPercent(
                      event
                        .target
                        .value,
                    )
                  }
                  type="number"
                  min="0.1"
                  max="10"
                  step="0.1"
                  placeholder="Risk %"
                  className="w-32 rounded-2xl border border-white/10 bg-white/[.03] px-4 py-3 outline-none"
                />


                <button
                  type="button"
                  disabled={
                    !entry ||
                    paperMutation
                      .isPending
                  }
                  onClick={
                    startPaperTrade
                  }
                  className="flex items-center gap-2 rounded-2xl bg-emerald-500 px-5 py-3 font-semibold disabled:opacity-50"
                >

                  {paperMutation
                    .isPending
                    ? (
                      <Loader2 className="size-4 animate-spin"/>
                    )
                    : (
                      <ShieldCheck className="size-4"/>
                    )}

                  Open Paper Trade

                </button>

              </div>

            </div>
          )}

        </section>
      )}


      <section className="premium-card rounded-3xl p-6">

        <h2 className="text-xl font-semibold">
          Recent AI Signals
        </h2>


        <div className="mt-5 space-y-3">

          {signalsQuery
            .isLoading && (
            <p className="text-sm text-slate-400">
              Loading signal history...
            </p>
          )}


          {signalsQuery
            .data
            ?.signals
            ?.map(
              signal => (
                <div
                  key={
                    signal.id
                  }
                  className="flex flex-col justify-between gap-4 rounded-2xl bg-white/[.03] p-4 md:flex-row md:items-center"
                >

                  <div>

                    <div className="flex items-center gap-3">

                      <span
                        className={[
                          "font-semibold",

                          signal.direction ===
                          "BUY"
                            ? "text-emerald-300"
                            : signal.direction ===
                              "SELL"
                            ? "text-red-300"
                            : "text-amber-300",

                        ].join(" ")}
                      >
                        {
                          signal.direction
                        }
                      </span>


                      <span className="font-medium">
                        {
                          signal.symbol
                        }
                      </span>


                      <span className="text-sm text-slate-500">
                        {
                          signal.timeframe
                        }
                      </span>

                    </div>


                    <p className="mt-2 text-xs text-slate-500">
                      {
                        new Date(
                          signal
                            .created_at,
                        )
                          .toLocaleString()
                      }
                    </p>

                  </div>


                  <div className="flex gap-6 text-sm">

                    <div>
                      <p className="text-slate-500">
                        Confidence
                      </p>

                      <p className="font-semibold">
                        {
                          signal.confidence
                        }%
                      </p>
                    </div>


                    <div>
                      <p className="text-slate-500">
                        Score
                      </p>

                      <p className="font-semibold">
                        {
                          signal.setup_score
                        }/100
                      </p>
                    </div>

                  </div>

                </div>
              ),
            )}


          {!signalsQuery
            .isLoading &&
            !signalsQuery
              .data
              ?.signals
              ?.length && (
            <p className="text-sm text-slate-500">
              No AI signals generated yet.
            </p>
          )}

        </div>

      </section>


      <section className="rounded-3xl border border-amber-400/20 bg-amber-400/[.05] p-5 text-sm leading-6 text-slate-400">

        <strong className="text-amber-200">
          Risk notice:
        </strong>{" "}

        AI analysis validates visible
        chart information against your
        strategy. It does not guarantee
        profitable trades. Paper trading
        should be used before enabling
        live execution.

      </section>

    </div>
  )
}
