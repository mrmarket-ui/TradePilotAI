import type { StrategyForm } from "@/hooks/useStrategyBuilder"
import ChipSelector from "@/components/strategy/ChipSelector"

type ConfirmationsStepProps = {
  data: {
    confirmations: string[]
  }
  update: (field: keyof StrategyForm, value: unknown) => void
}

const confirmationOptions = [
  "Higher Timeframe Trend Alignment",
  "Liquidity Taken",
  "Fair Value Gap Present",
  "Order Block Present",
  "Break of Structure Confirmed",
  "Market Structure Shift Confirmed",
  "Retest Confirmed",
  "Momentum Candle",
  "Volume Confirmation",
  "Session Confirmation",
  "Premium/Discount Alignment",
  "News Filter Passed",
  "Risk-Reward Requirement Met",
  "Trading Checklist Completed",
]

export default function ConfirmationsStep({
  data,
  update,
}: ConfirmationsStepProps) {
  return (
    <ChipSelector
      title="Required Confirmations"
      description="Choose the evidence TradePilot AI must verify before approving a setup."
      options={confirmationOptions}
      selected={data.confirmations}
      onChange={(confirmations) =>
        update("confirmations", confirmations)
      }
      allowCustom
      customPlaceholder="Add a custom confirmation"
    />
  )
}
