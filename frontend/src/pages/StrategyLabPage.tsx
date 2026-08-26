import {
  useMemo,
  useState,
} from "react"

import {
  BrainCircuit,
  Plus,
  RefreshCw,
  Search,
  Sparkles,
  ShieldCheck,
  Scale,
  Zap,
  SlidersHorizontal,
} from "lucide-react"

import StrategyCard from "@/components/strategy/StrategyCard"
import StrategyWizard from "@/components/strategy/StrategyWizard"
import { useStrategies } from "@/hooks/useStrategies"

import type {
  StrategyCreatePayload,
  StrategyProfile,
} from "@/types/strategy"

type TradingMode =
  | "conservative"
  | "balanced"
  | "aggressive"

const tradingModes = [
  {
    id: "conservative" as TradingMode,
    name: "Conservative",
    description:
      "Protect capital with lower risk, fewer trades and tighter daily limits.",
    risk: "0.5%",
    dailyLoss: "1.5%",
    trades: "2 / day",
    losses: "2",
    Icon: ShieldCheck,
  },
  {
    id: "balanced" as TradingMode,
    name: "Balanced",
    description:
      "Balance capital protection with enough flexibility to capture quality opportunities.",
    risk: "1.0%",
    dailyLoss: "2.0%",
    trades: "3 / day",
    losses: "2",
    Icon: Scale,
  },
  {
    id: "aggressive" as TradingMode,
    name: "Aggressive",
    description:
      "Use higher risk limits and more trading opportunities while keeping defined protection rules.",
    risk: "1.5%",
    dailyLoss: "3.0%",
    trades: "5 / day",
    losses: "3",
    Icon: Zap,
  },
] as const

function clonePayload(
  strategy: StrategyProfile,
): StrategyCreatePayload {
  return {
    name: `${strategy.name} Copy`,
    description:
      strategy.description || null,

    markets: [...strategy.markets],
    sessions: [...strategy.sessions],
    timeframes: [...strategy.timeframes],

    entry_rules: [
      ...strategy.entry_rules,
    ],
    exit_rules: [
      ...strategy.exit_rules,
    ],
    confirmations: [
      ...strategy.confirmations,
    ],

    psychology_rules: [
      ...strategy.psychology_rules,
    ],

    trade_management_rules: [
      ...strategy.trade_management_rules,
    ],

    max_risk_percent:
      strategy.max_risk_percent,

    max_daily_loss_percent:
      strategy.max_daily_loss_percent,

    max_weekly_loss_percent:
      strategy.max_weekly_loss_percent,

    max_trades_per_day:
      strategy.max_trades_per_day,

    max_consecutive_losses:
      strategy.max_consecutive_losses,

    requires_user_approval:
      strategy.requires_user_approval,

    is_active: false,
  }
}

export default function StrategyLabPage() {
  const {
    strategies,
    total,
    isLoading,
    isError,
    refetch,

    createStrategy,
    updateStrategy,
    deleteStrategy,
    activateStrategy,

    isCreating,
    isUpdating,
    isDeleting,
    isActivating,
  } = useStrategies()

  const [wizardOpen, setWizardOpen] =
    useState(false)

  const [
    editingStrategy,
    setEditingStrategy,
  ] =
    useState<StrategyProfile | null>(
      null,
    )

  const [search, setSearch] =
    useState("")

  const [message, setMessage] =
    useState("")

  const filteredStrategies = useMemo(
    () => {
      const query =
        search.trim().toLowerCase()

      if (!query) {
        return strategies
      }

      return strategies.filter(
        (strategy) =>
          [
            strategy.name,
            strategy.description,
            ...strategy.markets,
            ...strategy.sessions,
            ...strategy.timeframes,
          ]
            .filter(Boolean)
            .some((value) =>
              String(value)
                .toLowerCase()
                .includes(query),
            ),
      )
    },
    [search, strategies],
  )

  const activeStrategy =
    strategies.find(
      (strategy) =>
        strategy.is_active,
    ) || null

  function openNewStrategy() {
    setEditingStrategy(null)
    setMessage("")
    setWizardOpen(true)
  }

  async function createTradingMode(
    mode: TradingMode,
  ) {
    const presets: Record<
      TradingMode,
      StrategyCreatePayload
    > = {
      conservative: {
        name: "Conservative Strategy",

        description:
          "Capital protection focused framework that waits for stronger confirmation and limits trading frequency.",

        markets: [
          "Forex",
        ],

        sessions: [
          "London",
          "New York",
        ],

        timeframes: [
          "4H",
          "1H",
        ],

        entry_rules: [
          "Trade only in the direction of the higher timeframe market structure",
          "Wait for price to reach a clearly defined area of interest",
          "Enter only after a confirmed reaction from the area",
        ],

        exit_rules: [
          "Exit if the market structure invalidates the original setup",
          "Take profit at the planned target instead of extending the trade emotionally",
        ],

        confirmations: [
          "Higher timeframe direction must be clear",
          "Market structure must support the trade direction",
          "Price must show a clear rejection or confirmation before entry",
        ],

        psychology_rules: [
          "Do not revenge trade",
          "Do not chase missed entries",
          "Stop trading after reaching the consecutive loss limit",
        ],

        trade_management_rules: [
          "Risk no more than 0.5% per trade",
          "Maximum 2 trades per day",
          "Do not increase risk after a losing trade",
          "Protect capital before seeking additional opportunities",
        ],

        max_risk_percent: 0.5,
        max_daily_loss_percent: 1.5,
        max_weekly_loss_percent: 4,
        max_trades_per_day: 2,
        max_consecutive_losses: 2,

        requires_user_approval: true,
        is_active: false,
      },

      balanced: {
        name: "Balanced Strategy",

        description:
          "Balanced framework combining confirmation, reasonable trading frequency and controlled risk.",

        markets: [
          "Forex",
        ],

        sessions: [
          "London",
          "New York",
        ],

        timeframes: [
          "1H",
          "15M",
        ],

        entry_rules: [
          "Identify the primary market direction before searching for an entry",
          "Wait for a valid pullback or retracement into the planned trading area",
          "Enter after structure and momentum confirm the intended direction",
        ],

        exit_rules: [
          "Exit when the original setup becomes invalid",
          "Take profit at the predefined target or according to the strategy management rules",
        ],

        confirmations: [
          "Market structure must support the setup",
          "Entry area must align with the strategy",
          "A confirmation candle or structural reaction must appear before entry",
        ],

        psychology_rules: [
          "Only trade setups that meet the strategy rules",
          "Avoid revenge trading after a loss",
          "Do not force a trade because of fear of missing out",
        ],

        trade_management_rules: [
          "Risk no more than 1% per trade",
          "Maximum 3 trades per day",
          "Reduce unnecessary exposure when multiple setups are correlated",
          "Follow the original stop loss and target plan",
        ],

        max_risk_percent: 1,
        max_daily_loss_percent: 2,
        max_weekly_loss_percent: 5,
        max_trades_per_day: 3,
        max_consecutive_losses: 2,

        requires_user_approval: true,
        is_active: false,
      },

      aggressive: {
        name: "Aggressive Strategy",

        description:
          "Higher activity framework designed for experienced traders while maintaining strict loss protection.",

        markets: [
          "Forex",
        ],

        sessions: [
          "London",
          "New York",
        ],

        timeframes: [
          "15M",
          "5M",
        ],

        entry_rules: [
          "Confirm the short-term market structure before entering",
          "Trade only after price reacts from a valid setup area",
          "Use lower timeframe confirmation to refine the entry",
          "Avoid entries when structure is unclear or conflicting",
        ],

        exit_rules: [
          "Exit immediately when the setup structure is invalidated",
          "Take profit according to the predefined target plan",
          "Do not widen the stop loss after entry",
        ],

        confirmations: [
          "Short-term market structure must support the direction",
          "Momentum must support the intended trade",
          "Price must react clearly from the planned entry area",
        ],

        psychology_rules: [
          "Do not increase risk after a loss",
          "Respect the daily loss limit",
          "Do not overtrade simply because more setups are allowed",
          "Stop trading when emotional decision-making increases",
        ],

        trade_management_rules: [
          "Risk no more than 1.5% per trade",
          "Maximum 5 trades per day",
          "Never widen the stop loss to avoid taking a loss",
          "Reduce exposure after consecutive losses",
        ],

        max_risk_percent: 1.5,
        max_daily_loss_percent: 3,
        max_weekly_loss_percent: 7,
        max_trades_per_day: 5,
        max_consecutive_losses: 3,

        requires_user_approval: true,
        is_active: false,
      },
    }

    try {
      const strategy =
        await createStrategy(presets[mode])

      setMessage(
        `"${strategy.name}" created. Add your markets, entry rules and confirmations before activating it.`,
      )

      refetch()
    } catch {
      setMessage(
        "Unable to create the trading mode.",
      )
    }
  }

  function openEditStrategy(
    strategy: StrategyProfile,
  ) {
    setEditingStrategy(strategy)
    setMessage("")
    setWizardOpen(true)
  }

  async function submitStrategy(
    payload: StrategyCreatePayload,
  ) {
    if (editingStrategy) {
      return updateStrategy({
        strategyId:
          editingStrategy.id,
        payload,
      })
    }

    return createStrategy(payload)
  }

  async function cloneStrategy(
    strategy: StrategyProfile,
  ) {
    try {
      await createStrategy(
        clonePayload(strategy),
      )

      setMessage(
        `"${strategy.name}" was cloned successfully.`,
      )
    } catch {
      setMessage(
        "Unable to clone the strategy.",
      )
    }
  }

  async function removeStrategy(
    strategyId: number,
  ) {
    try {
      await deleteStrategy(strategyId)

      setMessage(
        "Strategy deleted successfully.",
      )
    } catch {
      setMessage(
        "Unable to delete the strategy.",
      )
    }
  }

  async function makeActive(
    strategyId: number,
  ) {
    try {
      await activateStrategy(strategyId)

      setMessage(
        "Active strategy updated.",
      )
    } catch {
      setMessage(
        "Unable to activate the strategy.",
      )
    }
  }

  if (wizardOpen) {
    return (
      <StrategyWizard
        key={
          editingStrategy?.id ||
          "new-strategy"
        }
        initialStrategy={
          editingStrategy
        }
        onCancel={() => {
          setWizardOpen(false)
          setEditingStrategy(null)
        }}
        onSubmit={submitStrategy}
        onSaved={(strategy) => {
          setWizardOpen(false)
          setEditingStrategy(null)

          setMessage(
            `"${strategy.name}" saved successfully.`,
          )

          refetch()
        }}
      />
    )
  }

  return (
    <div className="space-y-6">
      <section className="premium-card grid-surface rounded-[2rem] p-6 sm:p-8">
        <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-blue-300">
              Strategy Brain
            </p>

            <h2 className="mt-4 text-3xl font-semibold sm:text-4xl">
              Build the rules behind every decision.
            </h2>

            <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-400">
              Create, edit, clone and activate structured trading strategies.
            </p>
          </div>

          <button
            type="button"
            onClick={openNewStrategy}
            className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 px-5 py-3 text-sm font-semibold"
          >
            <Plus className="size-4" />
            New strategy
          </button>
        </div>
      </section>

      {message ? (
        <div className="rounded-2xl border border-blue-400/20 bg-blue-400/[0.07] px-4 py-3 text-sm text-blue-200">
          {message}
        </div>
      ) : null}

      <section className="premium-card rounded-[2rem] p-6 sm:p-8">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-indigo-300">
              Quick Start
            </p>

            <h3 className="mt-3 text-2xl font-semibold">
              Trading Modes
            </h3>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
              Start with a risk framework, then customize the strategy around your own trading rules.
            </p>
          </div>

          <button
            type="button"
            onClick={openNewStrategy}
            className="flex items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-2.5 text-sm font-semibold text-slate-300 transition hover:bg-white/[0.07]"
          >
            <SlidersHorizontal className="size-4" />
            Build my own
          </button>
        </div>

        <div className="mt-6 grid gap-4 lg:grid-cols-3">
          {tradingModes.map((mode) => {
            const Icon = mode.Icon

            const alreadyExists =
              strategies.some(
                (strategy) =>
                  strategy.name
                    .trim()
                    .toLowerCase() ===
                  `${mode.name} Strategy`
                    .toLowerCase(),
              )

            return (
              <article
                key={mode.id}
                className="rounded-3xl border border-white/10 bg-white/[0.025] p-5 transition hover:border-blue-400/25 hover:bg-white/[0.04]"
              >
                <div className="flex items-center gap-3">
                  <div className="grid size-11 place-items-center rounded-2xl bg-blue-400/[0.08] text-blue-300">
                    <Icon className="size-5" />
                  </div>

                  <div>
                    <h4 className="font-semibold">
                      {mode.name}
                    </h4>

                    <p className="text-xs text-slate-500">
                      Risk framework
                    </p>
                  </div>
                </div>

                <p className="mt-4 min-h-12 text-sm leading-6 text-slate-400">
                  {mode.description}
                </p>

                <div className="mt-5 grid grid-cols-2 gap-2 text-sm">
                  <div className="rounded-xl bg-white/[0.03] p-3">
                    <p className="text-xs text-slate-500">
                      Risk
                    </p>
                    <p className="mt-1 font-semibold">
                      {mode.risk}
                    </p>
                  </div>

                  <div className="rounded-xl bg-white/[0.03] p-3">
                    <p className="text-xs text-slate-500">
                      Daily loss
                    </p>
                    <p className="mt-1 font-semibold">
                      {mode.dailyLoss}
                    </p>
                  </div>

                  <div className="rounded-xl bg-white/[0.03] p-3">
                    <p className="text-xs text-slate-500">
                      Trades
                    </p>
                    <p className="mt-1 font-semibold">
                      {mode.trades}
                    </p>
                  </div>

                  <div className="rounded-xl bg-white/[0.03] p-3">
                    <p className="text-xs text-slate-500">
                      Loss stop
                    </p>
                    <p className="mt-1 font-semibold">
                      {mode.losses}
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  disabled={
                    isCreating ||
                    alreadyExists
                  }
                  onClick={() => {
                    if (!alreadyExists) {
                      createTradingMode(
                        mode.id,
                      )
                    }
                  }}
                  className={[
                    "mt-5 w-full rounded-2xl px-4 py-3 text-sm font-semibold transition disabled:cursor-not-allowed",
                    alreadyExists
                      ? "border border-emerald-400/15 bg-emerald-400/[0.07] text-emerald-300"
                      : "bg-blue-500/10 text-blue-300 hover:bg-blue-500/20 disabled:opacity-50",
                  ].join(" ")}
                >
                  {alreadyExists
                    ? "Already added"
                    : isCreating
                    ? "Creating..."
                    : `Use ${mode.name}`}
                </button>
              </article>
            )
          })}
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Saved strategies
          </p>

          <p className="mt-2 text-3xl font-semibold">
            {total}
          </p>
        </div>

        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Active strategy
          </p>

          <p className="mt-2 text-xl font-semibold text-emerald-300">
            {activeStrategy?.name || "None"}
          </p>
        </div>

        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Approval protection
          </p>

          <p className="mt-2 text-xl font-semibold text-blue-300">
            {activeStrategy
              ?.requires_user_approval
              ? "Required"
              : "Not configured"}
          </p>
        </div>
      </section>

      <label className="premium-card flex items-center gap-3 rounded-3xl px-4">
        <Search className="size-5 text-slate-500" />

        <input
          value={search}
          onChange={(event) =>
            setSearch(event.target.value)
          }
          placeholder="Search strategies, markets, sessions or timeframes..."
          className="w-full bg-transparent py-4 text-sm outline-none"
        />
      </label>

      {isLoading ? (
        <div className="grid min-h-96 place-items-center">
          Loading strategies...
        </div>
      ) : isError ? (
        <div className="premium-card rounded-3xl p-8">
          <p className="text-red-300">
            Unable to load strategies.
          </p>

          <button
            type="button"
            onClick={() => refetch()}
            className="mt-4 flex items-center gap-2 rounded-2xl border border-white/10 px-4 py-2"
          >
            <RefreshCw className="size-4" />
            Retry
          </button>
        </div>
      ) : filteredStrategies.length ? (
        <div className="space-y-5">
          {filteredStrategies.map(
            (strategy) => (
              <StrategyCard
                key={strategy.id}
                strategy={strategy}
                isActivating={isActivating}
                isDeleting={isDeleting}
                isCloning={isCreating}
                onEdit={openEditStrategy}
                onClone={cloneStrategy}
                onActivate={makeActive}
                onDelete={removeStrategy}
              />
            ),
          )}
        </div>
      ) : (
        <div className="premium-card grid min-h-96 place-items-center rounded-[2rem] p-8">
          <div className="text-center">
            <BrainCircuit className="mx-auto size-10 text-blue-300" />

            <h3 className="mt-4 text-xl font-semibold">
              No matching strategies
            </h3>

            <p className="mt-2 text-sm text-slate-500">
              Change your search or create a new strategy.
            </p>
          </div>
        </div>
      )}

      <aside className="premium-card rounded-3xl p-6">
        <div className="flex items-center gap-3">
          <Sparkles className="size-6 text-blue-300" />

          <h3 className="text-xl font-semibold">
            Strategy-aware AI
          </h3>
        </div>

        <p className="mt-3 text-sm leading-6 text-slate-400">
          The active strategy guides setup scoring, AI coaching and future chart analysis.
        </p>
      </aside>
    </div>
  )
}
