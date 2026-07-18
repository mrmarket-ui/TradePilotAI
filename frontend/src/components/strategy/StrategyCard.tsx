import {
  CheckCircle2,
  Pencil,
  Power,
  Trash2,
} from "lucide-react"

import type { StrategyProfile } from "@/types/strategy"

type StrategyCardProps = {
  strategy: StrategyProfile
  isActivating: boolean
  isDeleting: boolean
  onEdit: (strategy: StrategyProfile) => void
  onActivate: (strategyId: number) => void
  onDelete: (strategyId: number) => void
}

export default function StrategyCard({
  strategy,
  isActivating,
  isDeleting,
  onEdit,
  onActivate,
  onDelete,
}: StrategyCardProps) {
  return (
    <article
      className={[
        "premium-card rounded-3xl p-6",
        strategy.is_active
          ? "ring-1 ring-emerald-400/30"
          : "",
      ].join(" ")}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h3 className="text-xl font-semibold">
              {strategy.name}
            </h3>

            {strategy.is_active ? (
              <span className="flex items-center gap-1 rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300">
                <CheckCircle2 className="size-3.5" />
                Active
              </span>
            ) : null}
          </div>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            {strategy.description ||
              "No strategy description added."}
          </p>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => onEdit(strategy)}
            className="grid size-10 place-items-center rounded-2xl border border-white/10 bg-white/[0.03] text-slate-300 transition hover:bg-white/[0.07]"
            title="Edit strategy"
          >
            <Pencil className="size-4" />
          </button>

          <button
            type="button"
            onClick={() => {
              if (
                window.confirm(
                  `Delete "${strategy.name}"?`,
                )
              ) {
                onDelete(strategy.id)
              }
            }}
            disabled={isDeleting}
            className="grid size-10 place-items-center rounded-2xl border border-red-400/15 bg-red-400/[0.05] text-red-300 transition hover:bg-red-400/10 disabled:opacity-50"
            title="Delete strategy"
          >
            <Trash2 className="size-4" />
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-2xl border border-white/8 bg-white/[0.025] p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Markets
          </p>

          <p className="mt-2 text-sm font-medium text-slate-200">
            {strategy.markets.join(", ") || "None"}
          </p>
        </div>

        <div className="rounded-2xl border border-white/8 bg-white/[0.025] p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Timeframes
          </p>

          <p className="mt-2 text-sm font-medium text-slate-200">
            {strategy.timeframes.join(", ") || "None"}
          </p>
        </div>

        <div className="rounded-2xl border border-white/8 bg-white/[0.025] p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Risk per trade
          </p>

          <p className="mt-2 text-sm font-medium text-slate-200">
            {strategy.max_risk_percent}%
          </p>
        </div>

        <div className="rounded-2xl border border-white/8 bg-white/[0.025] p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Entry rules
          </p>

          <p className="mt-2 text-sm font-medium text-slate-200">
            {strategy.entry_rules.length}
          </p>
        </div>
      </div>

      <div className="mt-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div className="flex flex-wrap gap-2">
          {strategy.sessions.slice(0, 3).map((session) => (
            <span
              key={session}
              className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-xs text-slate-400"
            >
              {session}
            </span>
          ))}

          {strategy.confirmations.slice(0, 3).map(
            (confirmation) => (
              <span
                key={confirmation}
                className="rounded-full border border-blue-400/15 bg-blue-400/[0.05] px-3 py-1 text-xs text-blue-300"
              >
                {confirmation}
              </span>
            ),
          )}
        </div>

        {!strategy.is_active ? (
          <button
            type="button"
            onClick={() => onActivate(strategy.id)}
            disabled={isActivating}
            className="flex items-center justify-center gap-2 rounded-2xl border border-emerald-400/20 bg-emerald-400/[0.07] px-4 py-2.5 text-sm font-semibold text-emerald-300 transition hover:bg-emerald-400/10 disabled:opacity-50"
          >
            <Power className="size-4" />
            {isActivating
              ? "Activating..."
              : "Set active"}
          </button>
        ) : (
          <div className="rounded-2xl bg-emerald-400/[0.07] px-4 py-2.5 text-sm font-semibold text-emerald-300">
            Current strategy
          </div>
        )}
      </div>
    </article>
  )
}
