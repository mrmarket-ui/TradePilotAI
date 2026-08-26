import {
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  Copy,
  Loader2,
  Pencil,
  Power,
  Sparkles,
  Trash2,
} from "lucide-react"

import {
  useState,
} from "react"

import {
  reviewStrategy,
} from "@/api/strategy"

import type {
  StrategyProfile,
  StrategyReviewResponse,
} from "@/types/strategy"


type StrategyCardProps = {
  strategy: StrategyProfile
  isActivating: boolean
  isDeleting: boolean
  isCloning: boolean

  onEdit: (
    strategy: StrategyProfile,
  ) => void

  onClone: (
    strategy: StrategyProfile,
  ) => void

  onActivate: (
    strategyId: number,
  ) => void

  onDelete: (
    strategyId: number,
  ) => void
}


function getStrategyHealth(
  strategy: StrategyProfile,
) {
  let score = 0

  const issues: string[] = []

  if (strategy.markets.length > 0) {
    score += 10
  } else {
    issues.push(
      "Add at least one market.",
    )
  }

  if (strategy.timeframes.length > 0) {
    score += 10
  } else {
    issues.push(
      "Add at least one timeframe.",
    )
  }

  if (strategy.sessions.length > 0) {
    score += 5
  } else {
    issues.push(
      "Define preferred trading sessions.",
    )
  }

  if (strategy.entry_rules.length >= 2) {
    score += 20
  } else if (
    strategy.entry_rules.length === 1
  ) {
    score += 10

    issues.push(
      "Add more entry rules.",
    )
  } else {
    issues.push(
      "Entry rules are missing.",
    )
  }

  if (strategy.exit_rules.length >= 1) {
    score += 10
  } else {
    issues.push(
      "Exit rules are missing.",
    )
  }

  if (
    strategy.confirmations.length >= 2
  ) {
    score += 15
  } else if (
    strategy.confirmations.length === 1
  ) {
    score += 8

    issues.push(
      "Add another confirmation rule.",
    )
  } else {
    issues.push(
      "Confirmation rules are missing.",
    )
  }

  if (
    strategy.psychology_rules.length >= 1
  ) {
    score += 10
  } else {
    issues.push(
      "Add psychology protection rules.",
    )
  }

  if (
    strategy
      .trade_management_rules
      .length >= 1
  ) {
    score += 10
  } else {
    issues.push(
      "Add trade management rules.",
    )
  }

  if (
    strategy.max_risk_percent > 0 &&
    strategy.max_daily_loss_percent > 0 &&
    strategy.max_weekly_loss_percent > 0
  ) {
    score += 5
  } else {
    issues.push(
      "Complete the risk limits.",
    )
  }

  if (
    strategy.max_trades_per_day > 0 &&
    strategy.max_consecutive_losses > 0
  ) {
    score += 5
  } else {
    issues.push(
      "Complete daily trading limits.",
    )
  }

  const label =
    score >= 85
      ? "Strong"
      : score >= 70
      ? "Good"
      : score >= 50
      ? "Needs work"
      : "Weak"

  return {
    score,
    label,
    issues,
  }
}


export default function StrategyCard({
  strategy,
  isActivating,
  isDeleting,
  isCloning,
  onEdit,
  onClone,
  onActivate,
  onDelete,
}: StrategyCardProps) {
  const health =
    getStrategyHealth(strategy)

  const [
    aiReview,
    setAiReview,
  ] =
    useState<StrategyReviewResponse | null>(
      null,
    )

  const [
    reviewing,
    setReviewing,
  ] =
    useState(false)

  const [
    reviewError,
    setReviewError,
  ] =
    useState("")

  const [
    reviewOpen,
    setReviewOpen,
  ] =
    useState(false)


  async function runAIReview() {
    if (aiReview) {
      setReviewOpen(
        previous => !previous,
      )

      return
    }

    try {
      setReviewing(true)
      setReviewError("")

      const result =
        await reviewStrategy(
          strategy.id,
        )

      setAiReview(result)
      setReviewOpen(true)
    } catch (error: any) {
      const detail =
        error
          ?.response
          ?.data
          ?.detail

      const status =
        error?.response?.status

      const message =
        error?.message

      setReviewError(
        typeof detail === "string"
          ? detail
          : status
          ? `Review failed with HTTP ${status}.`
          : message
          ? `Review request failed: ${message}`
          : "Unable to review this strategy.",
      )
    } finally {
      setReviewing(false)
    }
  }


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

            <span
              className={[
                "rounded-full px-3 py-1 text-xs font-semibold",
                health.score >= 85
                  ? "bg-emerald-400/10 text-emerald-300"
                  : health.score >= 70
                  ? "bg-blue-400/10 text-blue-300"
                  : health.score >= 50
                  ? "bg-amber-400/10 text-amber-300"
                  : "bg-red-400/10 text-red-300",
              ].join(" ")}
            >
              Health {health.score}/100
            </span>
          </div>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            {strategy.description ||
              "No strategy description added."}
          </p>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() =>
              onEdit(strategy)
            }
            className="grid size-10 place-items-center rounded-2xl border border-white/10 bg-white/[0.03] text-slate-300 transition hover:bg-white/[0.07]"
            title="Edit strategy"
          >
            <Pencil className="size-4" />
          </button>

          <button
            type="button"
            onClick={() =>
              onClone(strategy)
            }
            disabled={isCloning}
            className="grid size-10 place-items-center rounded-2xl border border-blue-400/15 bg-blue-400/[0.05] text-blue-300 transition hover:bg-blue-400/10 disabled:opacity-50"
            title="Clone strategy"
          >
            <Copy className="size-4" />
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


      <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.02] p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
              Strategy Health
            </p>

            <p className="mt-1 text-lg font-semibold">
              {health.label}
            </p>
          </div>

          <p
            className={[
              "text-2xl font-bold",
              health.score >= 85
                ? "text-emerald-300"
                : health.score >= 70
                ? "text-blue-300"
                : health.score >= 50
                ? "text-amber-300"
                : "text-red-300",
            ].join(" ")}
          >
            {health.score}/100
          </p>
        </div>

        <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/[0.05]">
          <div
            className="h-full rounded-full bg-blue-500 transition-all"
            style={{
              width: `${health.score}%`,
            }}
          />
        </div>

        {health.issues.length > 0 ? (
          <div className="mt-4 flex items-start gap-3 rounded-2xl bg-amber-400/[0.05] p-3">
            <AlertTriangle className="mt-0.5 size-4 shrink-0 text-amber-300" />

            <div>
              <p className="text-sm font-medium text-amber-300">
                Improvement suggestion
              </p>

              <p className="mt-1 text-sm leading-6 text-slate-400">
                {health.issues[0]}
              </p>
            </div>
          </div>
        ) : null}
      </div>


      <div className="mt-5">
        <button
          type="button"
          onClick={runAIReview}
          disabled={reviewing}
          className="flex w-full items-center justify-center gap-2 rounded-2xl border border-indigo-400/20 bg-indigo-400/[0.07] px-4 py-3 text-sm font-semibold text-indigo-300 transition hover:bg-indigo-400/10 disabled:opacity-50"
        >
          {reviewing ? (
            <Loader2 className="size-4 animate-spin" />
          ) : (
            <Sparkles className="size-4" />
          )}

          {reviewing
            ? "Reviewing Strategy..."
            : aiReview
            ? reviewOpen
              ? "Hide AI Review"
              : "Show AI Review"
            : "Review with AI"}
        </button>

        {reviewError ? (
          <div className="mt-3 rounded-2xl border border-red-400/20 bg-red-400/[0.06] p-4 text-sm text-red-300">
            {reviewError}
          </div>
        ) : null}
      </div>


      {aiReview && reviewOpen ? (
        <section className="mt-5 rounded-3xl border border-indigo-400/15 bg-indigo-400/[0.035] p-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <BrainCircuit className="size-5 text-indigo-300" />

              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-indigo-300">
                  AI Strategy Review
                </p>

                <p className="mt-1 font-semibold">
                  {aiReview.grade}
                </p>
              </div>
            </div>

            <p className="text-3xl font-bold text-indigo-300">
              {aiReview.health_score}/100
            </p>
          </div>


          <p className="mt-5 text-sm leading-7 text-slate-300">
            {aiReview.summary}
          </p>


          <div className="mt-6 grid gap-4 lg:grid-cols-2">

            <div className="rounded-2xl bg-emerald-400/[0.04] p-4">
              <p className="font-semibold text-emerald-300">
                Strengths
              </p>

              <div className="mt-3 space-y-2">
                {aiReview.strengths.map(
                  (item) => (
                    <p
                      key={item}
                      className="text-sm leading-6 text-slate-400"
                    >
                      • {item}
                    </p>
                  ),
                )}
              </div>
            </div>


            <div className="rounded-2xl bg-red-400/[0.04] p-4">
              <p className="font-semibold text-red-300">
                Weaknesses
              </p>

              <div className="mt-3 space-y-2">
                {aiReview.weaknesses.map(
                  (item) => (
                    <p
                      key={item}
                      className="text-sm leading-6 text-slate-400"
                    >
                      • {item}
                    </p>
                  ),
                )}
              </div>
            </div>

          </div>


          {aiReview.missing_elements.length ? (
            <div className="mt-4 rounded-2xl border border-amber-400/10 bg-amber-400/[0.04] p-4">
              <p className="font-semibold text-amber-300">
                Missing Elements
              </p>

              <div className="mt-3 space-y-2">
                {aiReview.missing_elements.map(
                  (item) => (
                    <p
                      key={item}
                      className="text-sm leading-6 text-slate-400"
                    >
                      • {item}
                    </p>
                  ),
                )}
              </div>
            </div>
          ) : null}


          <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.025] p-4">
            <p className="font-semibold">
              Risk Assessment
            </p>

            <p className="mt-3 text-sm leading-7 text-slate-400">
              {aiReview.risk_assessment}
            </p>
          </div>


          <div className="mt-4 rounded-2xl border border-blue-400/10 bg-blue-400/[0.04] p-4">
            <p className="font-semibold text-blue-300">
              Priority Improvements
            </p>

            <div className="mt-3 space-y-3">
              {aiReview.priority_improvements.map(
                (item, index) => (
                  <div
                    key={item}
                    className="flex gap-3"
                  >
                    <span className="grid size-6 shrink-0 place-items-center rounded-full bg-blue-400/10 text-xs font-semibold text-blue-300">
                      {index + 1}
                    </span>

                    <p className="text-sm leading-6 text-slate-400">
                      {item}
                    </p>
                  </div>
                ),
              )}
            </div>
          </div>

        </section>
      ) : null}


      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Markets
          </p>

          <p className="mt-2 text-sm font-medium">
            {strategy.markets.join(", ") ||
              "None"}
          </p>
        </div>


        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Timeframes
          </p>

          <p className="mt-2 text-sm font-medium">
            {strategy.timeframes.join(", ") ||
              "None"}
          </p>
        </div>


        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Risk per trade
          </p>

          <p className="mt-2 text-sm font-medium">
            {strategy.max_risk_percent}%
          </p>
        </div>


        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Entry rules
          </p>

          <p className="mt-2 text-sm font-medium">
            {strategy.entry_rules.length}
          </p>
        </div>

      </div>


      <div className="mt-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">

        <div className="flex flex-wrap gap-2">

          {strategy.sessions
            .slice(0, 3)
            .map((session) => (
              <span
                key={session}
                className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-xs text-slate-400"
              >
                {session}
              </span>
            ))}


          {strategy.confirmations
            .slice(0, 3)
            .map((confirmation) => (
              <span
                key={confirmation}
                className="rounded-full border border-blue-400/15 bg-blue-400/[0.05] px-3 py-1 text-xs text-blue-300"
              >
                {confirmation}
              </span>
            ))}

        </div>


        {!strategy.is_active ? (
          <button
            type="button"
            onClick={() =>
              onActivate(strategy.id)
            }
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
