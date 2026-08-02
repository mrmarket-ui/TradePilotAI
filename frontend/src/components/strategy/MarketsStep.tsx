import type { StrategyForm } from "@/hooks/useStrategyBuilder"
import ChipSelector from "@/components/strategy/ChipSelector"

type MarketsStepProps = {
  data: {
    markets: string[]
  }
  update: (field: keyof StrategyForm, value: unknown) => void
}

const marketOptions = [
  "XAUUSD",
  "EURUSD",
  "GBPUSD",
  "USDJPY",
  "AUDUSD",
  "USDCAD",
  "NAS100",
  "US30",
  "SPX500",
  "DAX40",
  "BTCUSD",
  "ETHUSD",
]

export default function MarketsStep({
  data,
  update,
}: MarketsStepProps) {
  return (
    <ChipSelector
      title="Markets"
      description="Choose every market this strategy is allowed to trade."
      options={marketOptions}
      selected={data.markets}
      onChange={(markets) =>
        update("markets", markets)
      }
      allowCustom
      customPlaceholder="Add custom symbol, for example GER40"
    />
  )
}
