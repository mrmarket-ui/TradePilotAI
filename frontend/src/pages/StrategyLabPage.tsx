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
} from "lucide-react"

import StrategyCard from "@/components/strategy/StrategyCard"
import StrategyWizard from "@/components/strategy/StrategyWizard"
import { useStrategies } from "@/hooks/useStrategies"

import type {
  StrategyCreatePayload,
  StrategyProfile,
} from "@/types/strategy"

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
              Create, edit, clone and activate
              structured trading strategies.
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
                isActivating={
                  isActivating
                }
                isDeleting={isDeleting}
                isCloning={isCreating}
                onEdit={
                  openEditStrategy
                }
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
              Change your search or create a
              new strategy.
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
          The active strategy guides setup
          scoring, AI coaching and future chart
          analysis.
        </p>
      </aside>
    </div>
  )
}
