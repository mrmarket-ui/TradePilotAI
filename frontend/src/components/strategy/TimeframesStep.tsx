import type { StrategyForm } from "@/hooks/useStrategyBuilder"
import ChipSelector from "@/components/strategy/ChipSelector"

type TimeframesStepProps = {
  data: {
    timeframes: string[]
  }
  update: (field: keyof StrategyForm, value: unknown) => void
}

const timeframeOptions = [
  "M1",
  "M3",
  "M5",
  "M15",
  "M30",
  "H1",
  "H2",
  "H4",
  "D1",
  "W1",
]

export default function TimeframesStep({
  data,
  update,
}: TimeframesStepProps) {
  return (
    <ChipSelector
      title="Timeframes"
      description="Choose the execution and higher-timeframe charts used by this strategy."
      options={timeframeOptions}
      selected={data.timeframes}
      onChange={(timeframes) =>
        update("timeframes", timeframes)
      }
      allowCustom
      customPlaceholder="Add custom timeframe"
    />
  )
}
