import SetupScoreForm from "@/components/setup/SetupScoreForm"
import SetupScoreResult from "@/components/setup/SetupScoreResult"
import { useSetupScore } from "@/hooks/useSetupScore"

export default function SetupScorerPage() {
  const {
    scoreSetup,
    result,
    isScoring,
  } = useSetupScore()

  return (
    <div className="grid gap-8 xl:grid-cols-[420px_1fr]">

      <SetupScoreForm
        isLoading={isScoring}
        onSubmit={(
          strategyId,
          payload,
        ) =>
          scoreSetup({
            strategyId,
            payload,
          })
        }
      />

      {result ? (
        <SetupScoreResult
          result={result}
        />
      ) : (
        <div className="premium-card rounded-3xl p-8 grid place-items-center">
          <p className="text-slate-400">
            Score a setup to see the analysis.
          </p>
        </div>
      )}

    </div>
  )
}
