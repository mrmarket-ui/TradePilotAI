export type SetupScorePayload = {
  market: string
  session?: string | null
  timeframe?: string | null

  observed_entry_rules: string[]
  observed_confirmations: string[]

  risk_percent: number
  consecutive_losses: number
  trades_today: number

  user_emotion?: string | null
}

export type ScoreComponent = {
  name: string
  weight: number
  earned: number
  passed: boolean
  explanation: string
  matched: string[]
  missing: string[]
}

export type SetupScoreResponse = {
  strategy_id: number
  strategy_name: string

  overall_score: number
  verdict: string
  confidence: number

  components: ScoreComponent[]

  strengths: string[]
  weaknesses: string[]

  recommendation: string

  metadata: {
    component_count?: number
    [key: string]: unknown
  }
}
