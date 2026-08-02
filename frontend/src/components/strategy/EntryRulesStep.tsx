import type { StrategyForm } from "@/hooks/useStrategyBuilder"
import ChipSelector from "@/components/strategy/ChipSelector"

type EntryRulesStepProps = {
  data: {
    entry_rules: string[]
  }
  update: (field: keyof StrategyForm, value: unknown) => void
}

const entryRuleOptions = [
  "Liquidity Sweep",
  "Break of Structure",
  "Market Structure Shift",
  "Change of Character",
  "Fair Value Gap",
  "Order Block",
  "Mitigation Block",
  "Breaker Block",
  "Premium Zone",
  "Discount Zone",
  "SMT Divergence",
  "Higher Timeframe Bias",
  "Strong Displacement Candle",
  "Rejection Candle",
  "Volume Spike",
  "EMA Cross",
  "RSI Confirmation",
  "MACD Confirmation",
]

export default function EntryRulesStep({
  data,
  update,
}: EntryRulesStepProps) {
  return (
    <ChipSelector
      title="Entry Rules"
      description="Select every condition that must be present before this strategy allows an entry."
      options={entryRuleOptions}
      selected={data.entry_rules}
      onChange={(entryRules) =>
        update("entry_rules", entryRules)
      }
      allowCustom
      customPlaceholder="Add a custom entry rule"
    />
  )
}
