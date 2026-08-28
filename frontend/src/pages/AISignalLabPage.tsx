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


      <section className="premium-card rounded-3xl p-5 sm:p-6">

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
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-3 font-semibold disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
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
        <section className="space-y-5">

          {/* Main verdict */}
          <div
            className={[
              "premium-card overflow-hidden rounded-[2rem] border p-5 sm:p-8",

              current.direction === "BUY"
                ? "border-emerald-400/20"
                : current.direction === "SELL"
                ? "border-red-400/20"
                : "border-amber-400/20",

            ].join(" ")}
          >

            <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-start">

              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">
                  TradePilot AI Decision
                </p>

                <div className="mt-4 flex flex-wrap items-center gap-4">

                  <h2
                    className={[
                      "text-4xl font-bold tracking-tight sm:text-5xl",

                      current.direction === "BUY"
                        ? "text-emerald-300"
                        : current.direction === "SELL"
                        ? "text-red-300"
                        : "text-amber-300",

                    ].join(" ")}
                  >
                    {current.direction === "NO_TRADE"
                      ? "NO TRADE"
                      : current.direction}
                  </h2>

                  <span
                    className={[
                      "rounded-full border px-3 py-1 text-xs font-semibold",

                      current.confidence >= 60 &&
                      current.setup_score >= 60 &&
                      current.direction !== "NO_TRADE"
                        ? "border-emerald-400/20 bg-emerald-400/[0.07] text-emerald-300"
                        : "border-amber-400/20 bg-amber-400/[0.07] text-amber-300",

                    ].join(" ")}
                  >
                    {current.confidence >= 60 &&
                    current.setup_score >= 60 &&
                    current.direction !== "NO_TRADE"
                      ? "TradePilot threshold passed"
                      : "Setup rejected by threshold"}
                  </span>

                </div>

                <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-400">
                  {current.reasoning ||
                    "TradePilot analyzed the chart against the selected strategy and generated this decision."}
                </p>
              </div>


              <div className="grid w-full grid-cols-2 gap-3 lg:w-auto lg:min-w-[260px]">

                <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                  <p className="text-xs uppercase tracking-[0.15em] text-slate-500">
                    Symbol
                  </p>

                  <p className="mt-2 text-xl font-semibold">
                    {current.symbol}
                  </p>
                </div>

                <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                  <p className="text-xs uppercase tracking-[0.15em] text-slate-500">
                    Timeframe
                  </p>

                  <p className="mt-2 text-xl font-semibold">
                    {current.timeframe || "?"}
                  </p>
                </div>

              </div>

            </div>


            {/* Scores */}
            <div className="mt-8 grid gap-4 md:grid-cols-2">

              <div className="rounded-3xl border border-white/[0.07] bg-white/[0.025] p-5">

                <div className="flex items-center justify-between gap-4">

                  <div>
                    <p className="text-sm text-slate-400">
                      AI Confidence
                    </p>

                    <p className="mt-1 text-3xl font-semibold">
                      {Math.round(current.confidence)}%
                    </p>
                  </div>

                  <span className="text-xs text-slate-500">
                    Minimum 60%
                  </span>

                </div>

                <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/[0.05]">
                  <div
                    className={[
                      "h-full rounded-full transition-all duration-500",

                      current.confidence >= 60
                        ? "bg-emerald-400"
                        : "bg-amber-400",

                    ].join(" ")}
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(
                          0,
                          current.confidence,
                        ),
                      )}%`,
                    }}
                  />
                </div>

              </div>


              <div className="rounded-3xl border border-white/[0.07] bg-white/[0.025] p-5">

                <div className="flex items-center justify-between gap-4">

                  <div>
                    <p className="text-sm text-slate-400">
                      Setup Quality
                    </p>

                    <p className="mt-1 text-3xl font-semibold">
                      {Math.round(current.setup_score)}/100
                    </p>
                  </div>

                  <span className="text-xs text-slate-500">
                    Minimum 60
                  </span>

                </div>

                <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/[0.05]">
                  <div
                    className={[
                      "h-full rounded-full transition-all duration-500",

                      current.setup_score >= 60
                        ? "bg-blue-400"
                        : "bg-amber-400",

                    ].join(" ")}
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(
                          0,
                          current.setup_score,
                        ),
                      )}%`,
                    }}
                  />
                </div>

              </div>

            </div>

          </div>


          {/* Trade levels */}
          <div className="premium-card rounded-[2rem] p-6">

            <div className="flex flex-wrap items-center justify-between gap-4">

              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">
                  Trade Structure
                </p>

                <h3 className="mt-2 text-xl font-semibold">
                  Entry, protection and targets
                </h3>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-2 text-sm">
                Risk / Reward{" "}
                <strong className="ml-1 text-blue-300">
                  {current.risk_reward != null
                    ? `${formatNumber(current.risk_reward)}R`
                    : "?"}
                </strong>
              </div>

            </div>


            <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">

              <div className="rounded-2xl bg-white/[0.03] p-4">
                <p className="text-xs text-slate-500">
                  Entry Low
                </p>

                <p className="mt-2 font-semibold">
                  {formatNumber(
                    current.entry_low,
                  )}
                </p>
              </div>


              <div className="rounded-2xl bg-white/[0.03] p-4">
                <p className="text-xs text-slate-500">
                  Entry High
                </p>

                <p className="mt-2 font-semibold">
                  {formatNumber(
                    current.entry_high,
                  )}
                </p>
              </div>


              <div className="rounded-2xl border border-red-400/10 bg-red-400/[0.04] p-4">
                <p className="text-xs text-red-300/70">
                  Stop Loss
                </p>

                <p className="mt-2 font-semibold text-red-300">
                  {formatNumber(
                    current.stop_loss,
                  )}
                </p>
              </div>


              <div className="rounded-2xl border border-emerald-400/10 bg-emerald-400/[0.04] p-4">
                <p className="text-xs text-emerald-300/70">
                  TP1
                </p>

                <p className="mt-2 font-semibold text-emerald-300">
                  {formatNumber(
                    current.take_profit_1,
                  )}
                </p>
              </div>


              <div className="rounded-2xl border border-emerald-400/10 bg-emerald-400/[0.04] p-4">
                <p className="text-xs text-emerald-300/70">
                  TP2
                </p>

                <p className="mt-2 font-semibold text-emerald-300">
                  {formatNumber(
                    current.take_profit_2,
                  )}
                </p>
              </div>


              <div className="rounded-2xl border border-emerald-400/10 bg-emerald-400/[0.04] p-4">
                <p className="text-xs text-emerald-300/70">
                  TP3
                </p>

                <p className="mt-2 font-semibold text-emerald-300">
                  {formatNumber(
                    current.take_profit_3,
                  )}
                </p>
              </div>


              <div className="rounded-2xl bg-white/[0.03] p-4">
                <p className="text-xs text-slate-500">
                  R:R
                </p>

                <p className="mt-2 font-semibold">
                  {current.risk_reward != null
                    ? `1:${formatNumber(
                        current.risk_reward,
                      )}`
                    : "?"}
                </p>
              </div>

            </div>


            {current.entry_low == null &&
            current.entry_high == null &&
            current.stop_loss == null &&
            current.take_profit_1 == null ? (
              <p className="mt-5 rounded-2xl border border-dashed border-white/10 p-4 text-sm text-slate-500">
                TradePilot could not read reliable price levels from this screenshot, so no levels were invented.
              </p>
            ) : null}

          </div>


          {/* Strategy validation */}
          <div className="grid gap-5 xl:grid-cols-2">

            <div className="premium-card rounded-[2rem] p-6">

              <div className="flex items-center gap-3">
                <CheckCircle2 className="size-5 text-emerald-300"/>

                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">
                    Passed
                  </p>

                  <h3 className="mt-1 text-xl font-semibold">
                    Matched Strategy Rules
                  </h3>
                </div>
              </div>


              <div className="mt-5 space-y-3">

                {current.matched_rules?.length ? (
                  current.matched_rules.map(
                    (
                      rule,
                      index,
                    ) => (
                      <div
                        key={`${rule}-${index}`}
                        className="flex gap-3 rounded-2xl border border-emerald-400/10 bg-emerald-400/[0.04] p-4"
                      >
                        <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-300"/>

                        <span className="text-sm leading-6 text-slate-300">
                          {rule}
                        </span>
                      </div>
                    ),
                  )
                ) : (
                  <div className="rounded-2xl border border-dashed border-white/10 p-6 text-center text-sm text-slate-500">
                    No strategy rules were confidently matched.
                  </div>
                )}

              </div>

            </div>


            <div className="premium-card rounded-[2rem] p-6">

              <div className="flex items-center gap-3">
                <XCircle className="size-5 text-red-300"/>

                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-red-300">
                    Missing
                  </p>

                  <h3 className="mt-1 text-xl font-semibold">
                    Missing Confirmations
                  </h3>
                </div>
              </div>


              <div className="mt-5 space-y-3">

                {current.missing_rules?.length ? (
                  current.missing_rules.map(
                    (
                      rule,
                      index,
                    ) => (
                      <div
                        key={`${rule}-${index}`}
                        className="flex gap-3 rounded-2xl border border-red-400/10 bg-red-400/[0.04] p-4"
                      >
                        <XCircle className="mt-0.5 size-4 shrink-0 text-red-300"/>

                        <span className="text-sm leading-6 text-slate-300">
                          {rule}
                        </span>
                      </div>
                    ),
                  )
                ) : (
                  <div className="rounded-2xl border border-dashed border-white/10 p-6 text-center text-sm text-slate-500">
                    No required confirmations are currently missing.
                  </div>
                )}

              </div>

            </div>

          </div>


          {/* Explanation */}
          <div className="grid gap-5 xl:grid-cols-[1.3fr_0.7fr]">

            <div className="premium-card rounded-[2rem] p-6">

              <div className="flex items-center gap-3">
                <BrainCircuit className="size-5 text-blue-300"/>

                <h3 className="text-xl font-semibold">
                  Why TradePilot made this decision
                </h3>
              </div>

              <p className="mt-5 leading-7 text-slate-300">
                {current.reasoning ||
                  "No additional AI reasoning was returned for this signal."}
              </p>

            </div>


            <div className="premium-card rounded-[2rem] p-6">

              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-300">
                Invalidation
              </p>

              <h3 className="mt-2 text-xl font-semibold">
                What cancels this setup?
              </h3>

              <p className="mt-4 text-sm leading-7 text-slate-300">
                {current.invalidation ||
                  "No explicit invalidation condition was identified."}
              </p>

            </div>

          </div>


          {/* Paper trading */}
          <div className="premium-card rounded-[2rem] p-6">

            <div className="flex flex-col justify-between gap-5 md:flex-row md:items-center">

              <div>
                <div className="flex items-center gap-3">
                  <ShieldCheck className="size-5 text-emerald-300"/>

                  <h3 className="text-xl font-semibold">
                    Paper Trade Simulator
                  </h3>
                </div>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
                  Test qualified AI setups without risking real capital.
                </p>
              </div>


              <span
                className={[
                  "rounded-full border px-3 py-1 text-xs font-semibold",

                  current.direction !== "NO_TRADE" &&
                  current.confidence >= 60 &&
                  current.setup_score >= 60
                    ? "border-emerald-400/20 bg-emerald-400/[0.06] text-emerald-300"
                    : "border-amber-400/20 bg-amber-400/[0.06] text-amber-300",

                ].join(" ")}
              >
                {current.direction !== "NO_TRADE" &&
                current.confidence >= 60 &&
                current.setup_score >= 60
                  ? "Eligible for simulation"
                  : "Simulation locked"}
              </span>

            </div>


            {current.direction !== "NO_TRADE" &&
            current.confidence >= 60 &&
            current.setup_score >= 60 ? (

              <div className="mt-6 grid gap-3 sm:grid-cols-[minmax(0,1fr)_140px_auto]">

                <input
                  value={entry}
                  onChange={event =>
                    setEntry(
                      event.target.value,
                    )
                  }
                  type="number"
                  step="any"
                  placeholder="Entry price"
                  className="w-full min-w-0 rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 outline-none"
                />


                <input
                  value={riskPercent}
                  onChange={event =>
                    setRiskPercent(
                      event.target.value,
                    )
                  }
                  type="number"
                  min="0.1"
                  max="10"
                  step="0.1"
                  placeholder="Risk %"
                  className="w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 outline-none"
                />


                <button
                  type="button"
                  disabled={
                    !entry ||
                    paperMutation.isPending
                  }
                  onClick={startPaperTrade}
                  className="flex w-full items-center justify-center gap-2 rounded-2xl bg-emerald-500 px-5 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
                >

                  {paperMutation.isPending ? (
                    <Loader2 className="size-4 animate-spin"/>
                  ) : (
                    <ShieldCheck className="size-4"/>
                  )}

                  {paperMutation.isPending
                    ? "Opening..."
                    : "Send to Paper Trade"}

                </button>

              </div>

            ) : (

              <div className="mt-6 rounded-2xl border border-amber-400/10 bg-amber-400/[0.04] p-5">

                <p className="font-medium text-amber-300">
                  This setup cannot be paper traded.
                </p>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  TradePilot requires a BUY or SELL decision with at least 60% confidence and a setup score of at least 60.
                </p>

              </div>

            )}

          </div>

        </section>
      )}


      <section className="premium-card rounded-3xl p-5 sm:p-6">

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