import { useMemo, useState } from "react"
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  LoaderCircle,
  Save,
  X,
} from "lucide-react"

import AutomationStep from "@/components/strategy/AutomationStep"
import ConfirmationsStep from "@/components/strategy/ConfirmationsStep"
import EntryRulesStep from "@/components/strategy/EntryRulesStep"
import ExitRulesStep from "@/components/strategy/ExitRulesStep"
import GeneralStep from "@/components/strategy/GeneralStep"
import MarketsStep from "@/components/strategy/MarketsStep"
import PsychologyStep from "@/components/strategy/PsychologyStep"
import ReviewStep from "@/components/strategy/ReviewStep"
import RiskStep from "@/components/strategy/RiskStep"
import SessionsStep from "@/components/strategy/SessionsStep"
import TimeframesStep from "@/components/strategy/TimeframesStep"

import { type StrategyForm, useStrategyBuilder } from "@/hooks/useStrategyBuilder"

import type {
  StrategyCreatePayload,
  StrategyProfile,
} from "@/types/strategy"


type StrategyWizardProps = {
  initialStrategy?: StrategyProfile | null
  onCancel: () => void
  onSubmit: (
    payload: StrategyCreatePayload,
  ) => Promise<StrategyProfile>
  onSaved: (strategy: StrategyProfile) => void
}

const steps = [
  "General",
  "Markets",
  "Sessions",
  "Timeframes",
  "Entry Rules",
  "Exit Rules",
  "Confirmations",
  "Risk",
  "Psychology",
  "Automation",
  "Review",
]



function extractMinimumRiskReward(
  strategy: StrategyProfile,
): number {
  const extended = strategy as StrategyProfile & {
    min_risk_reward?: number
  }

  if (extended.min_risk_reward) {
    return extended.min_risk_reward
  }

  const rule =
    strategy.trade_management_rules?.find(
      (item) =>
        item.toLowerCase().includes(
          "risk-reward",
        ),
    )

  const match = rule?.match(/1:(\d+(?:\.\d+)?)/)

  return match ? Number(match[1]) : 2
}

function strategyToBuilderForm(
  strategy?: StrategyProfile | null,
): StrategyForm {
  const extended = strategy as
    | (StrategyProfile & {
        strategy_type?: string
        ai_setup_scoring_enabled?: boolean
      })
    | null
    | undefined

  return {
    name: strategy?.name || "",
    description:
      strategy?.description || "",
    strategy_type:
      extended?.strategy_type ||
      "Day Trading",

    markets: strategy?.markets || [],
    sessions: strategy?.sessions || [],
    timeframes: strategy?.timeframes || [],

    entry_rules:
      strategy?.entry_rules || [],
    exit_rules:
      strategy?.exit_rules || [],
    confirmations:
      strategy?.confirmations || [],
    psychology_rules:
      strategy?.psychology_rules || [],

    max_risk_percent:
      strategy?.max_risk_percent ?? 0.5,

    min_risk_reward:
      strategy
        ? extractMinimumRiskReward(strategy)
        : 2,

    max_trades_per_day:
      strategy?.max_trades_per_day ?? 3,

    requires_user_approval:
      strategy?.requires_user_approval ??
      true,

    ai_setup_scoring_enabled:
      extended?.ai_setup_scoring_enabled ??
      true,
  }
}
function validateStep(
  step: number,
  strategy: StrategyForm,
): string {
  switch (step) {
    case 0:
      if (strategy.name.trim().length < 2) {
        return "Enter a strategy name with at least two characters."
      }

      if (!strategy.strategy_type) {
        return "Choose a strategy type."
      }

      return ""

    case 1:
      return strategy.markets.length
        ? ""
        : "Select at least one market."

    case 2:
      return strategy.sessions.length
        ? ""
        : "Select at least one trading session."

    case 3:
      return strategy.timeframes.length
        ? ""
        : "Select at least one timeframe."

    case 4:
      return strategy.entry_rules.length
        ? ""
        : "Select or add at least one entry rule."

    case 5:
      return strategy.exit_rules.length
        ? ""
        : "Select or add at least one exit rule."

    case 6:
      return strategy.confirmations.length
        ? ""
        : "Select or add at least one confirmation."

    case 7:
      if (
        !Number.isFinite(strategy.max_risk_percent) ||
        strategy.max_risk_percent <= 0 ||
        strategy.max_risk_percent > 10
      ) {
        return "Risk per trade must be between 0.1% and 10%."
      }

      if (
        !Number.isFinite(strategy.min_risk_reward) ||
        strategy.min_risk_reward < 0.5
      ) {
        return "Minimum risk-reward must be at least 0.5."
      }

      if (
        !Number.isInteger(strategy.max_trades_per_day) ||
        strategy.max_trades_per_day < 1
      ) {
        return "Maximum trades per day must be at least 1."
      }

      return ""

    default:
      return ""
  }
}


function buildPayload(
  strategy: StrategyForm,
): StrategyCreatePayload {
  return {
    name: strategy.name.trim(),

    description:
      strategy.description.trim() || null,

    markets: strategy.markets,
    sessions: strategy.sessions,
    timeframes: strategy.timeframes,

    entry_rules: strategy.entry_rules,
    exit_rules: strategy.exit_rules,
    confirmations: strategy.confirmations,

    psychology_rules:
      strategy.psychology_rules,

    trade_management_rules: [
      `Minimum risk-reward 1:${strategy.min_risk_reward}`,
      `Maximum ${strategy.max_trades_per_day} trades per day`,
    ],

    max_risk_percent:
      strategy.max_risk_percent,

    max_daily_loss_percent: 2,
    max_weekly_loss_percent: 5,

    max_trades_per_day:
      strategy.max_trades_per_day,

    max_consecutive_losses: 2,

    requires_user_approval:
      strategy.requires_user_approval,

    is_active: true,
  }
}


export default function StrategyWizard({
  initialStrategy,
  onCancel,
  onSubmit,
  onSaved,
}: StrategyWizardProps) {
  const {
    step,
    next,
    back,
    strategy,
    update,
  } = useStrategyBuilder(
    strategyToBuilderForm(initialStrategy),
  )

  const [error, setError] = useState("")
  const [isSaving, setIsSaving] =
    useState(false)

  const progress = useMemo(
    () =>
      Math.round(
        ((step + 1) / steps.length) * 100,
      ),
    [step],
  )

  const isLastStep =
    step === steps.length - 1

  function continueToNextStep() {
    const validationError =
      validateStep(step, strategy)

    if (validationError) {
      setError(validationError)
      return
    }

    setError("")
    next()
  }

  function returnToPreviousStep() {
    setError("")
    back()
  }

  async function saveStrategy() {
    const requiredSteps = [
      0,
      1,
      2,
      3,
      4,
      5,
      6,
      7,
    ]

    for (const requiredStep of requiredSteps) {
      const validationError =
        validateStep(
          requiredStep,
          strategy,
        )

      if (validationError) {
        setError(validationError)
        return
      }
    }

    setError("")
    setIsSaving(true)

    try {
      const savedStrategy =
        await onSubmit(
          buildPayload(strategy),
        )

      onSaved(savedStrategy)
    } catch (requestError) {
      const possibleError =
        requestError as {
          response?: {
            data?: {
              detail?: string
            }
          }
          message?: string
        }

      setError(
        possibleError.response?.data?.detail ||
          possibleError.message ||
          "Unable to save the strategy.",
      )
    } finally {
      setIsSaving(false)
    }
  }

  const stepContent = [
    <GeneralStep
      key="general"
      data={strategy}
      update={update}
    />,

    <MarketsStep
      key="markets"
      data={strategy}
      update={update}
    />,

    <SessionsStep
      key="sessions"
      data={strategy}
      update={update}
    />,

    <TimeframesStep
      key="timeframes"
      data={strategy}
      update={update}
    />,

    <EntryRulesStep
      key="entry-rules"
      data={strategy}
      update={update}
    />,

    <ExitRulesStep
      key="exit-rules"
      data={strategy}
      update={update}
    />,

    <ConfirmationsStep
      key="confirmations"
      data={strategy}
      update={update}
    />,

    <RiskStep
      key="risk"
      data={strategy}
      update={update}
    />,

    <PsychologyStep
      key="psychology"
      data={strategy}
      update={update}
    />,

    <AutomationStep
      key="automation"
      data={strategy}
      update={update}
    />,

    <ReviewStep
      key="review"
      data={strategy}
    />,
  ]

  return (
    <div className="space-y-6">
      <section className="premium-card overflow-hidden rounded-[2rem]">
        <header className="border-b border-white/[0.07] p-5 sm:p-7">
          <div className="flex items-start justify-between gap-5">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-blue-300">
                Strategy Builder
              </p>

              <h1 className="mt-3 text-2xl font-semibold sm:text-3xl">
                {steps[step]}
              </h1>

              <p className="mt-2 text-sm text-slate-500">
                Step {step + 1} of{" "}
                {steps.length}
              </p>
            </div>

            <button
              type="button"
              onClick={onCancel}
              className="grid size-11 place-items-center rounded-2xl border border-white/10 bg-white/[0.03] text-slate-400 transition hover:bg-white/[0.07] hover:text-white"
              aria-label="Close strategy builder"
            >
              <X className="size-5" />
            </button>
          </div>

          <div className="mt-6 h-2 overflow-hidden rounded-full bg-white/[0.06]">
            <div
              className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-500"
              style={{
                width: `${progress}%`,
              }}
            />
          </div>

          <div className="mt-5 hidden gap-2 overflow-x-auto xl:flex">
            {steps.map(
              (stepName, index) => (
                <div
                  key={stepName}
                  className={[
                    "flex min-w-fit items-center gap-2 rounded-full border px-3 py-1.5 text-xs",
                    index === step
                      ? "border-blue-400/30 bg-blue-500/10 text-blue-300"
                      : index < step
                        ? "border-emerald-400/20 bg-emerald-400/[0.05] text-emerald-300"
                        : "border-white/[0.07] text-slate-600",
                  ].join(" ")}
                >
                  {index < step ? (
                    <CheckCircle2 className="size-3.5" />
                  ) : (
                    <span>
                      {index + 1}
                    </span>
                  )}

                  {stepName}
                </div>
              ),
            )}
          </div>
        </header>

        <main className="min-h-[520px] p-5 sm:p-7">
          {stepContent[step]}
        </main>

        <footer className="border-t border-white/[0.07] bg-black/10 p-5 sm:p-6">
          {error ? (
            <div className="mb-4 rounded-2xl border border-red-400/20 bg-red-400/[0.07] px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          ) : null}

          <div className="flex flex-col-reverse justify-between gap-3 sm:flex-row">
            <button
              type="button"
              onClick={
                step === 0
                  ? onCancel
                  : returnToPreviousStep
              }
              disabled={isSaving}
              className="flex items-center justify-center gap-2 rounded-2xl border border-white/10 px-5 py-3 text-sm font-semibold text-slate-300 transition hover:bg-white/[0.05] disabled:opacity-50"
            >
              <ArrowLeft className="size-4" />

              {step === 0
                ? "Cancel"
                : "Previous"}
            </button>

            {isLastStep ? (
              <button
                type="button"
                onClick={saveStrategy}
                disabled={isSaving}
                className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSaving ? (
                  <LoaderCircle className="size-4 animate-spin" />
                ) : (
                  <Save className="size-4" />
                )}

                {isSaving
                  ? "Saving strategy..."
                  : "Save strategy"}
              </button>
            ) : (
              <button
                type="button"
                onClick={continueToNextStep}
                className="flex items-center justify-center gap-2 rounded-2xl bg-blue-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-400"
              >
                Next step
                <ArrowRight className="size-4" />
              </button>
            )}
          </div>
        </footer>
      </section>
    </div>
  )
}
