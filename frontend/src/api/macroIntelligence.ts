import api from "@/api/client"

export type MacroClassification =
  | "STRONG"
  | "WEAK"
  | "INCONCLUSIVE"

export type MacroScoreComponent = {
  name: string
  score: number
  weight: number
  explanation: string
  available: boolean
}

export type NFPExtractedEvidence = {
  nfp_actual: number | null
  nfp_forecast: number | null
  nfp_previous: number | null
  nfp_revised_previous: number | null

  unemployment_actual: number | null
  unemployment_forecast: number | null
  unemployment_previous: number | null

  wage_mom_actual: number | null
  wage_mom_forecast: number | null
  wage_mom_previous: number | null

  wage_yoy_actual: number | null
  wage_yoy_forecast: number | null
  wage_yoy_previous: number | null

  evidence_notes: string[]
  uncertainties: string[]
}

export type MarketDirectionalBias = {
  market: string
  bias:
    | "BULLISH"
    | "BEARISH"
    | "MIXED"
    | "NEUTRAL"
  confidence: number
  explanation: string
}

export type DirectionalBias = {
  overall_context: string
  markets: MarketDirectionalBias[]
  disclaimer: string
}

export type NFPTextAnalysisResponse = {
  event: string
  classification: MacroClassification
  score: number
  confidence: number
  components: MacroScoreComponent[]
  strong_factors: string[]
  weak_factors: string[]
  contradictions: string[]
  warnings: string[]
  summary: string
  disclaimer: string
  extracted_evidence: NFPExtractedEvidence
  directional_bias?: DirectionalBias
  evidence_sources?: string[]
}

export async function analyzeNFPText(
  evidence: string,
): Promise<NFPTextAnalysisResponse> {
  const response =
    await api.post<NFPTextAnalysisResponse>(
      "/macro/analyze/nfp/text",
      { evidence },
    )

  return response.data
}

export async function analyzeNFPEvidence(
  evidence: string,
  images: File[] = [],
): Promise<NFPTextAnalysisResponse> {
  const formData = new FormData()

  if (evidence.trim()) {
    formData.append(
      "evidence",
      evidence.trim(),
    )
  }

  images.forEach((image) => {
    formData.append(
      "images",
      image,
    )
  })

  const response =
    await api.post<NFPTextAnalysisResponse>(
      "/macro/analyze/nfp/evidence",
      formData,
      {
        headers: {
          "Content-Type": undefined,
        },
      },
    )

  return response.data
}

export type GeneralMacroEvidenceItem = {
  indicator: string
  actual: string | null
  forecast: string | null
  previous: string | null
  unit: string | null
  category: string | null
  relevance:
    | "HIGH"
    | "MEDIUM"
    | "LOW"
    | "UNKNOWN"
  interpretation: string
}

export type GeneralMacroAnalysisResponse = {
  event: string
  currency: string | null
  classification:
    | "STRONG"
    | "POSITIVE"
    | "MIXED"
    | "WEAK"
    | "INCONCLUSIVE"
  confidence: number
  usd_bias:
    | "BULLISH"
    | "BEARISH"
    | "NEUTRAL"
    | "MIXED"
  usd_bias_confidence: number
  summary: string
  positive_factors: string[]
  negative_factors: string[]
  contradictions: string[]
  missing_information: string[]
  extracted_indicators: GeneralMacroEvidenceItem[]
  evidence_sources: string[]
  warnings: string[]
  disclaimer: string
}

export async function analyzeGeneralMacroEvidence(
  evidence: string,
  images: File[] = [],
): Promise<GeneralMacroAnalysisResponse> {
  const formData = new FormData()

  if (evidence.trim()) {
    formData.append(
      "evidence",
      evidence.trim(),
    )
  }

  images.forEach((image) => {
    formData.append(
      "images",
      image,
    )
  })

  const response =
    await api.post<GeneralMacroAnalysisResponse>(
      "/macro/analyze/general",
      formData,
      {
        headers: {
          "Content-Type": undefined,
        },
      },
    )

  return response.data
}

