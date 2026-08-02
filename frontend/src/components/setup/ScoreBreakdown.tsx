import type { ScoreComponent } from "@/types/setupScore"

type Props = {
  components: ScoreComponent[]
}

export default function ScoreBreakdown({
  components,
}: Props) {
  return (
    <div className="premium-card rounded-3xl p-6">
      <h2 className="text-xl font-semibold">
        Score Breakdown
      </h2>

      <div className="mt-6 space-y-4">
        {components.map((component) => (
          <div
            key={component.name}
            className="rounded-2xl border border-white/10 p-4"
          >
            <div className="flex items-center justify-between">
              <h3 className="font-medium">
                {component.name}
              </h3>

              <span
                className={
                  component.passed
                    ? "text-emerald-400"
                    : "text-red-400"
                }
              >
                {component.earned}/{component.weight}
              </span>
            </div>

            <p className="mt-2 text-sm text-slate-400">
              {component.explanation}
            </p>

            {component.matched.length > 0 && (
              <div className="mt-3">
                <p className="mb-2 text-xs uppercase tracking-wide text-emerald-300">
                  Matched
                </p>

                <div className="flex flex-wrap gap-2">
                  {component.matched.map((item) => (
                    <span
                      key={item}
                      className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-300"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {component.missing.length > 0 && (
              <div className="mt-3">
                <p className="mb-2 text-xs uppercase tracking-wide text-red-300">
                  Missing
                </p>

                <div className="flex flex-wrap gap-2">
                  {component.missing.map((item) => (
                    <span
                      key={item}
                      className="rounded-full bg-red-500/10 px-3 py-1 text-xs text-red-300"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
