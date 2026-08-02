import type { StrategyForm } from "@/hooks/useStrategyBuilder"
import ChipSelector from "@/components/strategy/ChipSelector"

type ExitRulesStepProps = {
  data: {
    exit_rules: string[]
  }
  update: (field: keyof StrategyForm, value: unknown) => void
}

const exitRuleOptions = [
  "Fixed Risk-Reward Target",
  "Take Profit at 2R",
  "Take Profit at 3R",
  "Opposing Liquidity",
  "Previous High",
  "Previous Low",
  "Close at Supply",
  "Close at Demand",
  "Partial Profit at 1R",
  "Move Stop to Break Even",
  "Trailing Stop",
  "Exit on Opposite Structure Shift",
  "Exit Before High-Impact News",
  "Time-Based Exit",
]

export default function ExitRulesStep({
  data,
  update,
}: ExitRulesStepProps) {
  return (
    <ChipSelector
      title="Exit Rules"
      description="Define how profitable and losing positions should be managed and closed."
      options={exitRuleOptions}
      selected={data.exit_rules}
      onChange={(exitRules) =>
        update("exit_rules", exitRules)
      }
      allowCustom
      customPlaceholder="Add a custom exit rule"
    />
  )
}
