import type {
  StrategyForm,
} from "@/hooks/useStrategyBuilder"

type RiskStepProps = {
  data: StrategyForm
  update: (
    field: keyof StrategyForm,
    value: unknown,
  ) => void
}

export default function RiskStep({
  data,
  update,
}: RiskStepProps) {
  const inputClass =
    "w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 outline-none transition focus:border-blue-400/40 focus:ring-4 focus:ring-blue-500/10"

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-3xl font-semibold">
          Risk Management
        </h2>

        <p className="mt-2 text-slate-400">
          Define the limits TradePilot AI must enforce
          when evaluating a setup.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-3">
        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Risk per trade %
          </span>

          <input
            type="number"
            min="0.1"
            max="10"
            step="0.1"
            value={data.max_risk_percent}
            onChange={(event) =>
              update(
                "max_risk_percent",
                Number(event.target.value),
              )
            }
            className={inputClass}
          />
        </label>

        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Minimum risk-reward
          </span>

          <input
            type="number"
            min="0.5"
            max="20"
            step="0.1"
            value={data.min_risk_reward}
            onChange={(event) =>
              update(
                "min_risk_reward",
                Number(event.target.value),
              )
            }
            className={inputClass}
          />
        </label>

        <label>
          <span className="mb-2 block text-sm text-slate-400">
            Maximum trades per day
          </span>

          <input
            type="number"
            min="1"
            max="100"
            value={data.max_trades_per_day}
            onChange={(event) =>
              update(
                "max_trades_per_day",
                Number(event.target.value),
              )
            }
            className={inputClass}
          />
        </label>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-3xl border border-blue-400/15 bg-blue-400/[0.05] p-5">
          <p className="text-sm text-slate-400">
            Maximum exposure
          </p>

          <p className="mt-2 text-3xl font-semibold text-blue-300">
            {data.max_risk_percent}%
          </p>
        </div>

        <div className="rounded-3xl border border-emerald-400/15 bg-emerald-400/[0.05] p-5">
          <p className="text-sm text-slate-400">
            Minimum target
          </p>

          <p className="mt-2 text-3xl font-semibold text-emerald-300">
            1:{data.min_risk_reward}
          </p>
        </div>

        <div className="rounded-3xl border border-amber-400/15 bg-amber-400/[0.05] p-5">
          <p className="text-sm text-slate-400">
            Daily trade limit
          </p>

          <p className="mt-2 text-3xl font-semibold text-amber-300">
            {data.max_trades_per_day}
          </p>
        </div>
      </div>
    </section>
  )
}
