import type { StrategyFormState } from "@/types/strategy"

type RiskSettingsProps = {
  form: StrategyFormState
  onChange: (next: StrategyFormState) => void
}

export default function RiskSettings({
  form,
  onChange,
}: RiskSettingsProps) {
  const inputClass =
    "w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm outline-none transition focus:border-blue-400/40 focus:ring-4 focus:ring-blue-500/10"

  return (
    <section className="premium-card rounded-3xl p-6">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-blue-300">
          Risk controls
        </p>

        <h3 className="mt-2 text-xl font-semibold">
          Protect the account before chasing profit
        </h3>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Risk per trade %
          </span>

          <input
            type="number"
            step="0.1"
            min="0.1"
            max="10"
            className={inputClass}
            value={form.max_risk_percent}
            onChange={(event) =>
              onChange({
                ...form,
                max_risk_percent: event.target.value,
              })
            }
          />
        </label>

        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Daily loss limit %
          </span>

          <input
            type="number"
            step="0.1"
            min="0.1"
            max="25"
            className={inputClass}
            value={form.max_daily_loss_percent}
            onChange={(event) =>
              onChange({
                ...form,
                max_daily_loss_percent:
                  event.target.value,
              })
            }
          />
        </label>

        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Weekly loss limit %
          </span>

          <input
            type="number"
            step="0.1"
            min="0.1"
            max="50"
            className={inputClass}
            value={form.max_weekly_loss_percent}
            onChange={(event) =>
              onChange({
                ...form,
                max_weekly_loss_percent:
                  event.target.value,
              })
            }
          />
        </label>

        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Max trades per day
          </span>

          <input
            type="number"
            min="1"
            max="100"
            className={inputClass}
            value={form.max_trades_per_day}
            onChange={(event) =>
              onChange({
                ...form,
                max_trades_per_day:
                  event.target.value,
              })
            }
          />
        </label>

        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Max consecutive losses
          </span>

          <input
            type="number"
            min="1"
            max="20"
            className={inputClass}
            value={form.max_consecutive_losses}
            onChange={(event) =>
              onChange({
                ...form,
                max_consecutive_losses:
                  event.target.value,
              })
            }
          />
        </label>
      </div>

      <label className="mt-6 flex items-start gap-3 rounded-2xl border border-white/10 bg-white/[0.025] p-4">
        <input
          type="checkbox"
          checked={form.requires_user_approval}
          onChange={(event) =>
            onChange({
              ...form,
              requires_user_approval:
                event.target.checked,
            })
          }
          className="mt-1 size-4"
        />

        <div>
          <p className="font-medium">
            Require user approval before execution
          </p>

          <p className="mt-1 text-sm leading-6 text-slate-500">
            TradePilot AI may prepare a setup, but the
            trader must approve it before any connected
            broker can receive an order.
          </p>
        </div>
      </label>
    </section>
  )
}
