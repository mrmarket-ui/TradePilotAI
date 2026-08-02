import { useState } from "react"

export type StrategyForm = {
  name: string
  description: string
  strategy_type: string

  markets: string[]
  sessions: string[]
  timeframes: string[]

  entry_rules: string[]
  exit_rules: string[]
  confirmations: string[]
  psychology_rules: string[]

  max_risk_percent: number
  min_risk_reward: number
  max_trades_per_day: number

  requires_user_approval: boolean
  ai_setup_scoring_enabled: boolean
}

export const initialStrategyForm: StrategyForm = {
  name: "",
  description: "",
  strategy_type: "Day Trading",

  markets: [],
  sessions: [],
  timeframes: [],

  entry_rules: [],
  exit_rules: [],
  confirmations: [],
  psychology_rules: [],

  max_risk_percent: 0.5,
  min_risk_reward: 2,
  max_trades_per_day: 3,

  requires_user_approval: true,
  ai_setup_scoring_enabled: true,
}

export function useStrategyBuilder(
  initialValue: StrategyForm =
    initialStrategyForm,
) {
  const [step, setStep] = useState(0)

  const [strategy, setStrategy] =
    useState<StrategyForm>(() => ({
      ...initialValue,
      markets: [...initialValue.markets],
      sessions: [...initialValue.sessions],
      timeframes: [...initialValue.timeframes],
      entry_rules: [...initialValue.entry_rules],
      exit_rules: [...initialValue.exit_rules],
      confirmations: [...initialValue.confirmations],
      psychology_rules: [
        ...initialValue.psychology_rules,
      ],
    }))

  function update(
    field: keyof StrategyForm,
    value: unknown,
  ) {
    setStrategy((previous) => ({
      ...previous,
      [field]: value,
    }))
  }

  function next() {
    setStep((previous) =>
      Math.min(previous + 1, 10),
    )
  }

  function back() {
    setStep((previous) =>
      Math.max(previous - 1, 0),
    )
  }

  return {
    step,
    next,
    back,
    strategy,
    update,
  }
}
