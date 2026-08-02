import {
  BrainCircuit,
  CheckCircle2,
  ShieldCheck,
  Target,
} from "lucide-react"

import type {
  StrategyForm,
} from "@/hooks/useStrategyBuilder"

type ReviewStepProps = {
  data: StrategyForm
}

function ReviewSection({
  title,
  items,
}: {
  title: string
  items: string[]
}) {
  return (
    <section className="rounded-3xl border border-white/[0.07] bg-white/[0.025] p-5">
      <h3 className="font-semibold">
        {title}
      </h3>

      {items.length ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {items.map((item) => (
            <span
              key={item}
              className="rounded-full border border-blue-400/20 bg-blue-400/[0.07] px-3 py-1.5 text-xs text-blue-300"
            >
              {item}
            </span>
          ))}
        </div>
      ) : (
        <p className="mt-3 text-sm text-slate-500">
          No options selected.
        </p>
      )}
    </section>
  )
}

export default function ReviewStep({
  data,
}: ReviewStepProps) {
  return (
    <section className="space-y-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-blue-300">
          Final review
        </p>

        <h2 className="mt-3 text-3xl font-semibold">
          Confirm your strategy
        </h2>

        <p className="mt-2 max-w-3xl text-slate-400">
          Review the rules TradePilot AI will use for
          setup scoring, coaching, risk checks and
          future chart analysis.
        </p>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <section className="rounded-3xl border border-white/[0.07] bg-white/[0.025] p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                Strategy
              </p>

              <h3 className="mt-2 text-2xl font-semibold">
                {data.name || "Unnamed strategy"}
              </h3>

              <p className="mt-2 text-sm text-blue-300">
                {data.strategy_type}
              </p>
            </div>

            <div className="grid size-12 place-items-center rounded-2xl bg-blue-400/10 text-blue-300">
              <BrainCircuit className="size-6" />
            </div>
          </div>

          <p className="mt-5 text-sm leading-6 text-slate-400">
            {data.description ||
              "No description added."}
          </p>
        </section>

        <section className="rounded-3xl border border-emerald-400/15 bg-emerald-400/[0.05] p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-emerald-300">
                Risk framework
              </p>

              <h3 className="mt-2 text-2xl font-semibold">
                Controlled execution
              </h3>
            </div>

            <ShieldCheck className="size-7 text-emerald-300" />
          </div>

          <div className="mt-5 grid grid-cols-3 gap-3">
            <div>
              <p className="text-xs text-slate-500">
                Risk
              </p>

              <p className="mt-1 text-xl font-semibold">
                {data.max_risk_percent}%
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-500">
                Minimum RR
              </p>

              <p className="mt-1 text-xl font-semibold">
                1:{data.min_risk_reward}
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-500">
                Daily trades
              </p>

              <p className="mt-1 text-xl font-semibold">
                {data.max_trades_per_day}
              </p>
            </div>
          </div>
        </section>
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <ReviewSection
          title="Markets"
          items={data.markets}
        />

        <ReviewSection
          title="Sessions"
          items={data.sessions}
        />

        <ReviewSection
          title="Timeframes"
          items={data.timeframes}
        />
      </div>

      <ReviewSection
        title="Entry rules"
        items={data.entry_rules}
      />

      <ReviewSection
        title="Exit rules"
        items={data.exit_rules}
      />

      <ReviewSection
        title="Required confirmations"
        items={data.confirmations}
      />

      <ReviewSection
        title="Psychology rules"
        items={data.psychology_rules}
      />

      <section className="rounded-3xl border border-white/[0.07] bg-white/[0.025] p-6">
        <div className="flex items-center gap-3">
          <Target className="size-5 text-blue-300" />

          <h3 className="font-semibold">
            AI controls
          </h3>
        </div>

        <div className="mt-5 space-y-3">
          <div className="flex items-center justify-between rounded-2xl bg-white/[0.03] px-4 py-3">
            <span className="text-sm text-slate-400">
              AI setup scoring
            </span>

            <span className={
              data.ai_setup_scoring_enabled
                ? "text-emerald-300"
                : "text-slate-500"
            }>
              {data.ai_setup_scoring_enabled
                ? "Enabled"
                : "Disabled"}
            </span>
          </div>

          <div className="flex items-center justify-between rounded-2xl bg-white/[0.03] px-4 py-3">
            <span className="text-sm text-slate-400">
              User approval
            </span>

            <span className={
              data.requires_user_approval
                ? "text-emerald-300"
                : "text-red-300"
            }>
              {data.requires_user_approval
                ? "Required"
                : "Disabled"}
            </span>
          </div>
        </div>
      </section>

      <div className="flex items-start gap-3 rounded-3xl border border-blue-400/15 bg-blue-400/[0.05] p-5">
        <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-blue-300" />

        <p className="text-sm leading-6 text-slate-400">
          Saving will create this strategy in your
          Strategy Brain database. It can then be
          activated, edited, scored and used by future
          Vision AI analysis.
        </p>
      </div>
    </section>
  )
}
