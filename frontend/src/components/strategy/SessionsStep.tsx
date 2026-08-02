import type { StrategyForm } from "@/hooks/useStrategyBuilder"
import ChipSelector from "@/components/strategy/ChipSelector"

type SessionsStepProps = {
  data: {
    sessions: string[]
  }
  update: (field: keyof StrategyForm, value: unknown) => void
}

const sessionOptions = [
  "Sydney",
  "Asia",
  "London",
  "New York",
  "London/New York overlap",
  "After-hours",
]

export default function SessionsStep({
  data,
  update,
}: SessionsStepProps) {
  return (
    <ChipSelector
      title="Trading Sessions"
      description="Select the sessions where this strategy is valid."
      options={sessionOptions}
      selected={data.sessions}
      onChange={(sessions) =>
        update("sessions", sessions)
      }
      allowCustom
      customPlaceholder="Add custom session or time window"
    />
  )
}
