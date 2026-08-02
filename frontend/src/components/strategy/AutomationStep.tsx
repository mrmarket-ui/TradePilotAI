import type {
  StrategyForm,
} from "@/hooks/useStrategyBuilder"

type AutomationStepProps = {
  data: StrategyForm
  update: (
    field: keyof StrategyForm,
    value: unknown,
  ) => void
}

type ToggleOption = {
  field:
    | "requires_user_approval"
    | "ai_setup_scoring_enabled"
  title: string
  description: string
  recommended?: boolean
}

const toggleOptions: ToggleOption[] = [
  {
    field: "ai_setup_scoring_enabled",
    title: "AI setup scoring",
    description:
      "Score every setup against this strategy before the trader enters.",
    recommended: true,
  },
  {
    field: "requires_user_approval",
    title: "Require user approval",
    description:
      "The AI may prepare a trade plan, but the user must approve it before execution.",
    recommended: true,
  },
]

export default function AutomationStep({
  data,
  update,
}: AutomationStepProps) {
  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-3xl font-semibold">
          AI and Automation
        </h2>

        <p className="mt-2 max-w-3xl text-slate-400">
          Choose how TradePilot AI should use this
          strategy. Approval-based automation is the
          safest option while broker execution remains
          under development.
        </p>
      </div>

      <div className="space-y-4">
        {toggleOptions.map((option) => {
          const enabled = Boolean(
            data[option.field],
          )

          return (
            <button
              key={option.field}
              type="button"
              onClick={() =>
                update(
                  option.field,
                  !enabled,
                )
              }
              className={[
                "flex w-full items-start justify-between gap-5 rounded-3xl border p-5 text-left transition",
                enabled
                  ? "border-blue-400/30 bg-blue-500/[0.08]"
                  : "border-white/10 bg-white/[0.025] hover:bg-white/[0.045]",
              ].join(" ")}
            >
              <div>
                <div className="flex flex-wrap items-center gap-3">
                  <h3 className="text-lg font-semibold">
                    {option.title}
                  </h3>

                  {option.recommended ? (
                    <span className="rounded-full border border-emerald-400/20 bg-emerald-400/[0.07] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-emerald-300">
                      Recommended
                    </span>
                  ) : null}
                </div>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
                  {option.description}
                </p>
              </div>

              <span
                className={[
                  "relative mt-1 h-7 w-12 shrink-0 rounded-full transition",
                  enabled
                    ? "bg-blue-500"
                    : "bg-slate-700",
                ].join(" ")}
              >
                <span
                  className={[
                    "absolute top-1 size-5 rounded-full bg-white transition",
                    enabled
                      ? "left-6"
                      : "left-1",
                  ].join(" ")}
                />
              </span>
            </button>
          )
        })}
      </div>

      <div className="rounded-3xl border border-amber-400/15 bg-amber-400/[0.05] p-5">
        <p className="font-semibold text-amber-300">
          Safety rule
        </p>

        <p className="mt-2 text-sm leading-6 text-slate-400">
          Do not enable unattended trade execution
          until broker adapters, maximum-loss guards,
          duplicate-order prevention and an emergency
          stop have been fully tested.
        </p>
      </div>
    </section>
  )
}
