import ScoreBreakdown from "./ScoreBreakdown"
import ScoreGauge from "./ScoreGauge"
import ScoreStrengths from "./ScoreStrengths"
import ScoreWeaknesses from "./ScoreWeaknesses"

import type {
  SetupScoreResponse,
} from "@/types/setupScore"

type Props = {
  result: SetupScoreResponse
}

export default function SetupScoreResult({
  result,
}: Props) {
  return (
    <div className="space-y-6">

      <ScoreGauge
        score={result.overall_score}
      />

      <div className="premium-card rounded-3xl p-6">
        <div className="flex items-center justify-between">

          <div>

            <p className="text-sm text-slate-400">
              Verdict
            </p>

            <h2 className="mt-2 text-3xl font-bold">
              {result.verdict}
            </h2>

          </div>

          <div className="text-right">

            <p className="text-sm text-slate-400">
              Confidence
            </p>

            <h2 className="mt-2 text-3xl font-bold text-blue-400">
              {result.confidence}%
            </h2>

          </div>

        </div>

        <p className="mt-6 text-slate-300 leading-7">
          {result.recommendation}
        </p>

      </div>

      <div className="grid gap-6 lg:grid-cols-2">

        <ScoreStrengths
          strengths={result.strengths}
        />

        <ScoreWeaknesses
          weaknesses={result.weaknesses}
        />

      </div>

      <ScoreBreakdown
        components={result.components}
      />

    </div>
  )
}
