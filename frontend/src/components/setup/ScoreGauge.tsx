type Props = {
  score: number
}

export default function ScoreGauge({
  score,
}: Props) {
  const percentage = Math.max(
    0,
    Math.min(score, 100),
  )

  return (
    <div className="premium-card rounded-3xl p-6">
      <p className="text-sm text-slate-400">
        Overall Score
      </p>

      <div className="mt-4">
        <div className="h-4 overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-blue-500 transition-all duration-700"
            style={{
              width: `${percentage}%`,
            }}
          />
        </div>

        <h2 className="mt-6 text-5xl font-bold">
          {score}
          <span className="text-xl text-slate-400">
            /100
          </span>
        </h2>
      </div>
    </div>
  )
}
