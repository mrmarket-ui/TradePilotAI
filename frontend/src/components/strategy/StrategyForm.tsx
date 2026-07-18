import {
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react"

import {
  Check,
  Plus,
  Save,
  X,
} from "lucide-react"

import RuleSelector from "@/components/strategy/RuleSelector"
import RiskSettings from "@/components/strategy/RiskSettings"

import type {
  StrategyFormState,
  StrategyProfile,
} from "@/types/strategy"

import {
  emptyStrategyForm,
  formToStrategyPayload,
  strategyToForm,
} from "@/types/strategy"


type StrategyFormProps = {
  strategy?: StrategyProfile | null
  isSaving: boolean
  onCancel: () => void
  onSubmit: (
    payload: ReturnType<
      typeof formToStrategyPayload
    >,
  ) => Promise<void>
}


const marketOptions = [
  "XAUUSD",
  "EURUSD",
  "GBPUSD",
  "USDJPY",
  "NAS100",
  "US30",
  "BTCUSD",
]

const sessionOptions = [
  "Asia",
  "London",
  "New York",
  "London/New York overlap",
]

const timeframeOptions = [
  "M1",
  "M5",
  "M15",
  "M30",
  "H1",
  "H4",
  "D1",
]

const entryRuleOptions = [
  "Liquidity sweep",
  "Break of structure",
  "Change of character",
  "Fair value gap",
  "Order block",
  "Supply zone",
  "Demand zone",
  "Premium/discount alignment",
  "Trend continuation",
  "Market structure shift",
]

const exitRuleOptions = [
  "Take profit at 2R",
  "Take profit at 3R",
  "Close at supply",
  "Close at demand",
  "Partial profit at 1R",
  "Trailing stop",
  "Exit on opposite structure shift",
]

const confirmationOptions = [
  "Retest",
  "Momentum candle",
  "Volume confirmation",
  "Session confirmation",
  "Premium/discount confirmation",
  "Higher-timeframe alignment",
  "News filter passed",
]

const psychologyOptions = [
  "No revenge trading",
  "No trading after two losses",
  "No trading while frustrated",
  "No news trading",
  "No Friday afternoon trading",
  "Follow pre-trade checklist",
  "Stop after daily target",
]

const managementOptions = [
  "Move stop loss to breakeven at 1R",
  "Take partial profit at 1R",
  "Trail behind structure",
  "Do not widen stop loss",
  "Close before high-impact news",
  "One position per setup",
]


function normalizeCustomValue(
  value: string,
) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
}


function addUniqueValues(
  current: string[],
  values: string[],
) {
  const merged = [...current]

  values.forEach((value) => {
    if (!merged.includes(value)) {
      merged.push(value)
    }
  })

  return merged
}


export default function StrategyForm({
  strategy,
  isSaving,
  onCancel,
  onSubmit,
}: StrategyFormProps) {
  const [form, setForm] =
    useState<StrategyFormState>(
      emptyStrategyForm,
    )

  const [error, setError] = useState("")
  const [customEntryRule, setCustomEntryRule] =
    useState("")
  const [customExitRule, setCustomExitRule] =
    useState("")
  const [
    customConfirmation,
    setCustomConfirmation,
  ] = useState("")

  useEffect(() => {
    if (strategy) {
      setForm(strategyToForm(strategy))
    } else {
      setForm(emptyStrategyForm)
    }

    setError("")
  }, [strategy])

  const selectedSummary = useMemo(
    () => ({
      markets: form.markets.length,
      timeframes: form.timeframes.length,
      rules:
        form.entry_rules.length +
        form.confirmations.length,
    }),
    [form],
  )

  async function submit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()
    setError("")

    if (form.name.trim().length < 2) {
      setError(
        "Strategy name must contain at least 2 characters.",
      )
      return
    }

    if (!form.markets.length) {
      setError(
        "Select at least one market.",
      )
      return
    }

    if (!form.timeframes.length) {
      setError(
        "Select at least one timeframe.",
      )
      return
    }

    if (!form.entry_rules.length) {
      setError(
        "Select or add at least one entry rule.",
      )
      return
    }

    const payload =
      formToStrategyPayload(form)

    try {
      await onSubmit(payload)
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to save strategy.",
      )
    }
  }

  function addCustomEntryRule() {
    const values =
      normalizeCustomValue(
        customEntryRule,
      )

    if (!values.length) {
      return
    }

    setForm({
      ...form,
      entry_rules: addUniqueValues(
        form.entry_rules,
        values,
      ),
    })

    setCustomEntryRule("")
  }

  function addCustomExitRule() {
    const values =
      normalizeCustomValue(
        customExitRule,
      )

    if (!values.length) {
      return
    }

    setForm({
      ...form,
      exit_rules: addUniqueValues(
        form.exit_rules,
        values,
      ),
    })

    setCustomExitRule("")
  }

  function addCustomConfirmation() {
    const values =
      normalizeCustomValue(
        customConfirmation,
      )

    if (!values.length) {
      return
    }

    setForm({
      ...form,
      confirmations:
        addUniqueValues(
          form.confirmations,
          values,
        ),
    })

    setCustomConfirmation("")
  }

  const inputClass =
    "w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm outline-none transition focus:border-blue-400/40 focus:ring-4 focus:ring-blue-500/10"

  return (
    <form
      onSubmit={submit}
      className="space-y-6"
    >
      <section className="premium-card rounded-[2rem] p-6 sm:p-8">
        <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-start">
          <div>
            <p className="text-xs uppercase tracking-[0.22em] text-blue-300">
              {strategy
                ? "Edit strategy"
                : "New strategy"}
            </p>

            <h2 className="mt-3 text-3xl font-semibold">
              {strategy
                ? strategy.name
                : "Build your trading playbook"}
            </h2>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
              Define the exact markets,
              confirmations, psychology rules
              and risk controls TradePilot AI
              must use when evaluating setups.
            </p>
          </div>

          <button
            type="button"
            onClick={onCancel}
            className="grid size-11 place-items-center rounded-2xl border border-white/10 bg-white/[0.03] text-slate-300"
          >
            <X className="size-5" />
          </button>
        </div>

        <div className="mt-8 grid gap-4 lg:grid-cols-[1fr_1.5fr]">
          <label>
            <span className="mb-2 block text-sm text-slate-400">
              Strategy name
            </span>

            <input
              value={form.name}
              onChange={(event) =>
                setForm({
                  ...form,
                  name: event.target.value,
                })
              }
              className={inputClass}
              placeholder="London Breakout"
            />
          </label>

          <label>
            <span className="mb-2 block text-sm text-slate-400">
              Description
            </span>

            <input
              value={form.description}
              onChange={(event) =>
                setForm({
                  ...form,
                  description:
                    event.target.value,
                })
              }
              className={inputClass}
              placeholder="Gold breakout strategy for the London session."
            />
          </label>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-white/8 bg-white/[0.025] p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
              Markets
            </p>

            <p className="mt-2 text-2xl font-semibold">
              {selectedSummary.markets}
            </p>
          </div>

          <div className="rounded-2xl border border-white/8 bg-white/[0.025] p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
              Timeframes
            </p>

            <p className="mt-2 text-2xl font-semibold">
              {selectedSummary.timeframes}
            </p>
          </div>

          <div className="rounded-2xl border border-white/8 bg-white/[0.025] p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
              Decision rules
            </p>

            <p className="mt-2 text-2xl font-semibold">
              {selectedSummary.rules}
            </p>
          </div>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-3">
        <RuleSelector
          title="Markets"
          options={marketOptions}
          selected={form.markets}
          onChange={(markets) =>
            setForm({
              ...form,
              markets,
            })
          }
        />

        <RuleSelector
          title="Sessions"
          options={sessionOptions}
          selected={form.sessions}
          onChange={(sessions) =>
            setForm({
              ...form,
              sessions,
            })
          }
        />

        <RuleSelector
          title="Timeframes"
          options={timeframeOptions}
          selected={form.timeframes}
          onChange={(timeframes) =>
            setForm({
              ...form,
              timeframes,
            })
          }
        />
      </div>

      <RuleSelector
        title="Entry rules"
        options={entryRuleOptions}
        selected={form.entry_rules}
        onChange={(entry_rules) =>
          setForm({
            ...form,
            entry_rules,
          })
        }
      />

      <div className="premium-card rounded-3xl p-6">
        <p className="text-sm font-semibold">
          Add custom entry rules
        </p>

        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <input
            value={customEntryRule}
            onChange={(event) =>
              setCustomEntryRule(
                event.target.value,
              )
            }
            className={inputClass}
            placeholder="Example: sweep previous day low"
          />

          <button
            type="button"
            onClick={addCustomEntryRule}
            className="flex items-center justify-center gap-2 rounded-2xl border border-blue-400/20 bg-blue-400/[0.07] px-5 py-3 text-sm font-semibold text-blue-300"
          >
            <Plus className="size-4" />
            Add rule
          </button>
        </div>
      </div>

      <RuleSelector
        title="Exit rules"
        options={exitRuleOptions}
        selected={form.exit_rules}
        onChange={(exit_rules) =>
          setForm({
            ...form,
            exit_rules,
          })
        }
      />

      <div className="premium-card rounded-3xl p-6">
        <p className="text-sm font-semibold">
          Add custom exit rules
        </p>

        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <input
            value={customExitRule}
            onChange={(event) =>
              setCustomExitRule(
                event.target.value,
              )
            }
            className={inputClass}
            placeholder="Example: exit if M5 structure reverses"
          />

          <button
            type="button"
            onClick={addCustomExitRule}
            className="flex items-center justify-center gap-2 rounded-2xl border border-blue-400/20 bg-blue-400/[0.07] px-5 py-3 text-sm font-semibold text-blue-300"
          >
            <Plus className="size-4" />
            Add rule
          </button>
        </div>
      </div>

      <RuleSelector
        title="Required confirmations"
        options={confirmationOptions}
        selected={form.confirmations}
        onChange={(confirmations) =>
          setForm({
            ...form,
            confirmations,
          })
        }
      />

      <div className="premium-card rounded-3xl p-6">
        <p className="text-sm font-semibold">
          Add custom confirmations
        </p>

        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <input
            value={customConfirmation}
            onChange={(event) =>
              setCustomConfirmation(
                event.target.value,
              )
            }
            className={inputClass}
            placeholder="Example: H1 bullish order flow"
          />

          <button
            type="button"
            onClick={addCustomConfirmation}
            className="flex items-center justify-center gap-2 rounded-2xl border border-blue-400/20 bg-blue-400/[0.07] px-5 py-3 text-sm font-semibold text-blue-300"
          >
            <Plus className="size-4" />
            Add confirmation
          </button>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <RuleSelector
          title="Psychology rules"
          options={psychologyOptions}
          selected={
            form.psychology_rules
          }
          onChange={(
            psychology_rules,
          ) =>
            setForm({
              ...form,
              psychology_rules,
            })
          }
        />

        <RuleSelector
          title="Trade management"
          options={managementOptions}
          selected={
            form.trade_management_rules
          }
          onChange={(
            trade_management_rules,
          ) =>
            setForm({
              ...form,
              trade_management_rules,
            })
          }
        />
      </div>

      <RiskSettings
        form={form}
        onChange={setForm}
      />

      <label className="premium-card flex items-start gap-3 rounded-3xl p-5">
        <input
          type="checkbox"
          checked={form.is_active}
          onChange={(event) =>
            setForm({
              ...form,
              is_active:
                event.target.checked,
            })
          }
          className="mt-1 size-4"
        />

        <div>
          <p className="flex items-center gap-2 font-semibold">
            <Check className="size-4 text-emerald-300" />
            Make this the active strategy
          </p>

          <p className="mt-1 text-sm leading-6 text-slate-500">
            The active strategy will be used
            automatically by chart analysis,
            AI coaching and setup scoring.
          </p>
        </div>
      </label>

      {error ? (
        <div className="rounded-2xl border border-red-400/20 bg-red-400/[0.07] px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      ) : null}

      <div className="sticky bottom-4 z-10 flex flex-col justify-end gap-3 rounded-3xl border border-white/10 bg-[#090f1c]/95 p-4 shadow-2xl backdrop-blur-xl sm:flex-row">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-2xl border border-white/10 px-6 py-3 text-sm font-semibold text-slate-300"
        >
          Cancel
        </button>

        <button
          type="submit"
          disabled={isSaving}
          className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 disabled:opacity-50"
        >
          <Save className="size-4" />

          {isSaving
            ? "Saving strategy..."
            : strategy
              ? "Save changes"
              : "Create strategy"}
        </button>
      </div>
    </form>
  )
}
