import ChipSelector from "@/components/strategy/ChipSelector"

import type {
  StrategyForm,
} from "@/hooks/useStrategyBuilder"

type PsychologyStepProps = {
  data: StrategyForm
  update: (
    field: keyof StrategyForm,
    value: unknown,
  ) => void
}

const psychologyOptions = [
  "No Revenge Trading",
  "No FOMO",
  "No Emotional Entries",
  "Follow Pre-Trade Checklist",
  "Journal Every Trade",
  "Daily Review Required",
  "Stop After Two Consecutive Losses",
  "Do Not Increase Lot Size After a Loss",
  "No Trading While Frustrated",
  "No Trading When Tired",
  "Accept Losses Without Hesitation",
  "Wait for Full Confirmation",
  "Stop After Daily Target",
  "No High-Impact News Trading",
]

export default function PsychologyStep({
  data,
  update,
}: PsychologyStepProps) {
  return (
    <ChipSelector
      title="Psychology Rules"
      description="Choose the discipline and emotional-control rules this strategy requires."
      options={psychologyOptions}
      selected={data.psychology_rules}
      onChange={(rules) =>
        update("psychology_rules", rules)
      }
      allowCustom
      customPlaceholder="Add a custom psychology rule"
    />
  )
}
