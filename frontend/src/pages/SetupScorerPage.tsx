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
    <div className="grid min-w-0 gap-6 lg:gap-8 xl:grid-cols-[minmax(0,420px)_minmax(0,1fr)]">

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
        <div className="premium-card grid min-h-64 place-items-center rounded-3xl p-5 text-center sm:min-h-80 sm:p-8">
          <p className="text-slate-400">
            Score a setup to see the analysis.
          </p>
        </div>
      )}

    </div>
  )
}

