import { useState } from "react"
import {
  BrainCircuit,
  Plus,
  RefreshCw,
  Sparkles,
} from "lucide-react"

import StrategyCard from "@/components/strategy/StrategyCard"
import StrategyForm from "@/components/strategy/StrategyForm"
import { useStrategies } from "@/hooks/useStrategies"

import type {
  StrategyCreatePayload,
  StrategyProfile,
} from "@/types/strategy"


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

  const [formOpen, setFormOpen] =
    useState(false)

  const [editingStrategy, setEditingStrategy] =
    useState<StrategyProfile | null>(null)


  function openNewStrategy() {
    setEditingStrategy(null)
    setFormOpen(true)
  }


  function openEditStrategy(
    strategy: StrategyProfile,
  ) {
    setEditingStrategy(strategy)
    setFormOpen(true)
  }


  async function saveStrategy(
    payload: StrategyCreatePayload,
  ) {
    if (editingStrategy) {
      await updateStrategy({
        strategyId: editingStrategy.id,
        payload,
      })
    } else {
      await createStrategy(payload)
    }

    setFormOpen(false)
    setEditingStrategy(null)
  }


  async function removeStrategy(
    strategyId: number,
  ) {
    await deleteStrategy(strategyId)
  }


  async function makeActive(
    strategyId: number,
  ) {
    await activateStrategy(strategyId)
  }


  if (formOpen) {
    return (
      <StrategyForm
        strategy={editingStrategy}
        isSaving={
          isCreating ||
          isUpdating
        }
        onCancel={() => {
          setFormOpen(false)
          setEditingStrategy(null)
        }}
        onSubmit={saveStrategy}
      />
    )
  }


  return (
    <div className="space-y-6">
      <section className="premium-card grid-surface overflow-hidden rounded-[2rem] p-6 sm:p-8">
        <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-blue-300">
              Strategy Brain
            </p>

            <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
              Teach TradePilot AI exactly how you trade.
            </h2>

            <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-400">
              Build structured trading strategies with
              markets, sessions, entry rules,
              confirmations, psychology controls and
              risk limits. The active strategy becomes
              the foundation for chart analysis,
              setup scoring and AI coaching.
            </p>
          </div>

          <button
            onClick={openNewStrategy}
            className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20"
          >
            <Plus className="size-4" />
            New strategy
          </button>
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
            {
              strategies.find(
                (strategy) =>
                  strategy.is_active,
              )?.name || "None"
            }
          </p>
        </div>

        <div className="premium-card rounded-3xl p-5">
          <p className="text-sm text-slate-500">
            Approval mode
          </p>

          <p className="mt-2 text-xl font-semibold text-blue-300">
            {
              strategies.find(
                (strategy) =>
                  strategy.is_active,
              )?.requires_user_approval
                ? "Required"
                : "Not configured"
            }
          </p>
        </div>
      </section>


      <section className="grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
        <div>
          {isLoading ? (
            <div className="grid min-h-[420px] place-items-center">
              <div className="text-center">
                <div className="mx-auto size-10 animate-spin rounded-full border-2 border-blue-400/20 border-t-blue-400" />

                <p className="mt-4 text-sm text-slate-400">
                  Loading strategies...
                </p>
              </div>
            </div>
          ) : isError ? (
            <div className="premium-card rounded-[2rem] p-8">
              <p className="text-red-300">
                Unable to load strategies.
              </p>

              <button
                onClick={() => refetch()}
                className="mt-4 flex items-center gap-2 rounded-2xl border border-white/10 px-4 py-2 text-sm"
              >
                <RefreshCw className="size-4" />
                Retry
              </button>
            </div>
          ) : strategies.length ? (
            <div className="space-y-5">
              {strategies.map((strategy) => (
                <StrategyCard
                  key={strategy.id}
                  strategy={strategy}
                  isActivating={isActivating}
                  isDeleting={isDeleting}
                  onEdit={openEditStrategy}
                  onActivate={makeActive}
                  onDelete={removeStrategy}
                />
              ))}
            </div>
          ) : (
            <div className="premium-card grid min-h-[420px] place-items-center rounded-[2rem] p-8">
              <div className="max-w-md text-center">
                <div className="mx-auto grid size-16 place-items-center rounded-3xl bg-blue-500/10 text-blue-300">
                  <BrainCircuit className="size-8" />
                </div>

                <h3 className="mt-6 text-2xl font-semibold">
                  Create your first strategy
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-500">
                  Define your markets, timeframes,
                  entry rules and risk controls so
                  TradePilot AI can evaluate setups
                  according to your own trading style.
                </p>

                <button
                  onClick={openNewStrategy}
                  className="mt-6 inline-flex items-center gap-2 rounded-2xl bg-blue-500 px-5 py-3 text-sm font-semibold"
                >
                  <Plus className="size-4" />
                  Build strategy
                </button>
              </div>
            </div>
          )}
        </div>


        <aside className="space-y-5">
          <div className="premium-card rounded-3xl p-6">
            <div className="grid size-12 place-items-center rounded-2xl bg-blue-500/10 text-blue-300">
              <Sparkles className="size-6" />
            </div>

            <h3 className="mt-5 text-xl font-semibold">
              Strategy-aware AI
            </h3>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              TradePilot AI will compare chart
              observations and trade setups against
              the active strategy rather than giving
              generic trading advice.
            </p>
          </div>

          <div className="premium-card rounded-3xl p-6">
            <p className="text-xs uppercase tracking-[0.2em] text-amber-300">
              Next module
            </p>

            <h3 className="mt-3 text-xl font-semibold">
              Chart analysis
            </h3>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Upload a TradingView or MT5 screenshot,
              identify observed rules and receive a
              strategy match score with a clear
              verdict.
            </p>
          </div>

          <div className="rounded-3xl border border-emerald-400/15 bg-emerald-400/[0.05] p-6">
            <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">
              Safety
            </p>

            <p className="mt-3 text-sm leading-6 text-slate-300">
              Keep user approval enabled. Automated
              execution must remain disabled until a
              real broker adapter, risk guard and
              emergency stop are tested.
            </p>
          </div>
        </aside>
      </section>
    </div>
  )
}
