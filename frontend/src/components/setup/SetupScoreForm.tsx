import {
  useEffect,
  useMemo,
  useState,
} from "react"

import {
  CheckCircle2,
  LoaderCircle,
  Target,
} from "lucide-react"

import { useStrategies } from "@/hooks/useStrategies"

import type {
  StrategyProfile,
} from "@/types/strategy"

import type {
  SetupScorePayload,
} from "@/types/setupScore"


type Props = {
  onSubmit: (
    strategyId: number,
    payload: SetupScorePayload,
  ) => Promise<unknown> | void

  isLoading: boolean
}


function toggleItem(
  current: string[],
  item: string,
): string[] {
  return current.includes(item)
    ? current.filter(
        (value) => value !== item,
      )
    : [...current, item]
}


function RuleSelector({
  title,
  items,
  selected,
  onToggle,
}: {
  title: string
  items: string[]
  selected: string[]
  onToggle: (item: string) => void
}) {
  return (
    <section>
      <div className="flex items-center justify-between gap-3">
        <h3 className="font-semibold">
          {title}
        </h3>

        <span className="text-xs text-slate-500">
          {selected.length}/{items.length} selected
        </span>
      </div>

      {items.length ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {items.map((item) => {
            const active =
              selected.includes(item)

            return (
              <button
                key={item}
                type="button"
                onClick={() =>
                  onToggle(item)
                }
                className={[
                  "flex items-center gap-2 rounded-2xl border px-3 py-2 text-xs font-medium transition",
                  active
                    ? "border-blue-400/30 bg-blue-500/15 text-blue-200"
                    : "border-white/10 bg-white/[0.03] text-slate-400 hover:border-blue-400/20 hover:text-white",
                ].join(" ")}
              >
                {active ? (
                  <CheckCircle2 className="size-3.5" />
                ) : null}

                {item}
              </button>
            )
          })}
        </div>
      ) : (
        <p className="mt-3 rounded-2xl border border-dashed border-white/10 p-4 text-sm text-slate-500">
          No rules were saved for this strategy.
        </p>
      )}
    </section>
  )
}


export default function SetupScoreForm({
  onSubmit,
  isLoading,
}: Props) {
  const {
    strategies,
    isLoading: strategiesLoading,
  } = useStrategies()

  const [strategyId, setStrategyId] =
    useState(0)

  const [market, setMarket] =
    useState("")

  const [session, setSession] =
    useState("")

  const [timeframe, setTimeframe] =
    useState("")

  const [
    selectedEntryRules,
    setSelectedEntryRules,
  ] = useState<string[]>([])

  const [
    selectedConfirmations,
    setSelectedConfirmations,
  ] = useState<string[]>([])

  const [risk, setRisk] =
    useState(0.5)

  const [tradesToday, setTradesToday] =
    useState(0)

  const [
    consecutiveLosses,
    setConsecutiveLosses,
  ] = useState(0)

  const [emotion, setEmotion] =
    useState("focused")

  const [error, setError] =
    useState("")

  const selectedStrategy =
    useMemo<StrategyProfile | null>(
      () =>
        strategies.find(
          (strategy) =>
            strategy.id === strategyId,
        ) || null,
      [strategies, strategyId],
    )

  useEffect(() => {
    if (
      strategyId !== 0 ||
      !strategies.length
    ) {
      return
    }

    const active =
      strategies.find(
        (strategy) =>
          strategy.is_active,
      ) || strategies[0]

    setStrategyId(active.id)
  }, [strategies, strategyId])

  useEffect(() => {
    if (!selectedStrategy) {
      return
    }

    setMarket(
      selectedStrategy.markets[0] || "",
    )

    setSession(
      selectedStrategy.sessions[0] || "",
    )

    setTimeframe(
      selectedStrategy.timeframes[0] || "",
    )

    setRisk(
      selectedStrategy.max_risk_percent,
    )

    setSelectedEntryRules([])
    setSelectedConfirmations([])
    setError("")
  }, [selectedStrategy])

  async function submit() {
    if (!selectedStrategy) {
      setError(
        "Select a strategy before scoring.",
      )
      return
    }

    if (!market) {
      setError("Select a market.")
      return
    }

    if (!session) {
      setError("Select a session.")
      return
    }

    if (!timeframe) {
      setError("Select a timeframe.")
      return
    }

    if (
      !Number.isFinite(risk) ||
      risk <= 0
    ) {
      setError(
        "Enter a valid risk percentage.",
      )
      return
    }

    setError("")

    await onSubmit(
      selectedStrategy.id,
      {
        market,
        session,
        timeframe,

        observed_entry_rules:
          selectedEntryRules,

        observed_confirmations:
          selectedConfirmations,

        risk_percent: risk,

        consecutive_losses:
          consecutiveLosses,

        trades_today: tradesToday,

        user_emotion: emotion,
      },
    )
  }

  const inputClass =
    "w-full rounded-2xl border border-white/10 bg-[#0b1120] px-4 py-3 text-sm outline-none transition focus:border-blue-400/40 focus:ring-4 focus:ring-blue-500/10"

  if (strategiesLoading) {
    return (
      <div className="premium-card grid min-h-96 place-items-center rounded-[2rem] p-6">
        <div className="text-center">
          <LoaderCircle className="mx-auto size-7 animate-spin text-blue-300" />

          <p className="mt-3 text-sm text-slate-400">
            Loading strategies...
          </p>
        </div>
      </div>
    )
  }

  if (!strategies.length) {
    return (
      <div className="premium-card grid min-h-96 place-items-center rounded-[2rem] p-8">
        <div className="max-w-sm text-center">
          <Target className="mx-auto size-10 text-blue-300" />

          <h2 className="mt-4 text-xl font-semibold">
            No strategies available
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-500">
            Create a strategy in Strategy Lab
            before scoring a setup.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="premium-card space-y-6 rounded-[2rem] p-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-300">
          Pre-trade validation
        </p>

        <h2 className="mt-3 text-2xl font-semibold">
          Score My Setup
        </h2>
      </div>

      <label>
        <span className="mb-2 block text-sm text-slate-400">
          Strategy
        </span>

        <select
          className={inputClass}
          value={strategyId}
          onChange={(event) =>
            setStrategyId(
              Number(event.target.value),
            )
          }
        >
          {strategies.map(
            (strategy) => (
              <option
                key={strategy.id}
                value={strategy.id}
              >
                {strategy.name}
                {strategy.is_active
                  ? " — Active"
                  : ""}
              </option>
            ),
          )}
        </select>
      </label>

      <div className="grid gap-4 sm:grid-cols-3">
        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Market
          </span>

          <select
            className={inputClass}
            value={market}
            onChange={(event) =>
              setMarket(event.target.value)
            }
          >
            {selectedStrategy?.markets.map(
              (item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ),
            )}
          </select>
        </label>

        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Session
          </span>

          <select
            className={inputClass}
            value={session}
            onChange={(event) =>
              setSession(event.target.value)
            }
          >
            {selectedStrategy?.sessions.map(
              (item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ),
            )}
          </select>
        </label>

        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Timeframe
          </span>

          <select
            className={inputClass}
            value={timeframe}
            onChange={(event) =>
              setTimeframe(event.target.value)
            }
          >
            {selectedStrategy?.timeframes.map(
              (item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ),
            )}
          </select>
        </label>
      </div>

      <RuleSelector
        title="Observed Entry Rules"
        items={
          selectedStrategy?.entry_rules || []
        }
        selected={selectedEntryRules}
        onToggle={(item) =>
          setSelectedEntryRules(
            (current) =>
              toggleItem(current, item),
          )
        }
      />

      <RuleSelector
        title="Observed Confirmations"
        items={
          selectedStrategy?.confirmations || []
        }
        selected={selectedConfirmations}
        onToggle={(item) =>
          setSelectedConfirmations(
            (current) =>
              toggleItem(current, item),
          )
        }
      />

      <div className="grid gap-4 sm:grid-cols-2">
        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Risk percentage
          </span>

          <input
            type="number"
            min="0.1"
            max="100"
            step="0.1"
            className={inputClass}
            value={risk}
            onChange={(event) =>
              setRisk(
                Number(event.target.value),
              )
            }
          />
        </label>

        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Emotional state
          </span>

          <select
            className={inputClass}
            value={emotion}
            onChange={(event) =>
              setEmotion(event.target.value)
            }
          >
            <option value="calm">Calm</option>
            <option value="focused">Focused</option>
            <option value="confident">Confident</option>
            <option value="disciplined">Disciplined</option>
            <option value="anxious">Anxious</option>
            <option value="frustrated">Frustrated</option>
            <option value="revenge">Revenge mindset</option>
            <option value="fomo">FOMO</option>
          </select>
        </label>

        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Trades taken today
          </span>

          <input
            type="number"
            min="0"
            className={inputClass}
            value={tradesToday}
            onChange={(event) =>
              setTradesToday(
                Number(event.target.value),
              )
            }
          />
        </label>

        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Consecutive losses
          </span>

          <input
            type="number"
            min="0"
            className={inputClass}
            value={consecutiveLosses}
            onChange={(event) =>
              setConsecutiveLosses(
                Number(event.target.value),
              )
            }
          />
        </label>
      </div>

      {error ? (
        <div className="rounded-2xl border border-red-400/20 bg-red-400/[0.07] px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      ) : null}

      <button
        type="button"
        onClick={submit}
        disabled={isLoading}
        className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 py-3.5 font-semibold disabled:opacity-50"
      >
        {isLoading ? (
          <>
            <LoaderCircle className="size-4 animate-spin" />
            Scoring setup...
          </>
        ) : (
          <>
            <Target className="size-4" />
            Score setup
          </>
        )}
      </button>
    </div>
  )
}
