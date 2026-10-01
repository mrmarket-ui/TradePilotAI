from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


class NFPAnalysisRequest(BaseModel):
    """
    Structured US Non-Farm Payrolls evidence.

    Payroll figures are expressed in thousands.
    Percentage fields use normal percentage values,
    for example 4.1 for 4.1%.
    """

    nfp_actual: float | None = None
    nfp_forecast: float | None = None
    nfp_previous: float | None = None
    nfp_revised_previous: float | None = None

    unemployment_actual: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    unemployment_forecast: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    unemployment_previous: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    wage_mom_actual: float | None = Field(
        default=None,
        ge=-20,
        le=20,
    )
    wage_mom_forecast: float | None = Field(
        default=None,
        ge=-20,
        le=20,
    )
    wage_mom_previous: float | None = Field(
        default=None,
        ge=-20,
        le=20,
    )

    wage_yoy_actual: float | None = Field(
        default=None,
        ge=-50,
        le=50,
    )
    wage_yoy_forecast: float | None = Field(
        default=None,
        ge=-50,
        le=50,
    )
    wage_yoy_previous: float | None = Field(
        default=None,
        ge=-50,
        le=50,
    )


class MacroScoreComponentResponse(BaseModel):
    name: str
    score: float
    weight: float
    explanation: str
    available: bool


class NFPAnalysisResponse(BaseModel):
    event: str

    classification: Literal[
        "STRONG",
        "WEAK",
        "INCONCLUSIVE",
    ]

    score: float = Field(
        ge=-100,
        le=100,
    )

    confidence: float = Field(
        ge=0,
        le=100,
    )

    components: list[
        MacroScoreComponentResponse
    ] = Field(
        default_factory=list,
    )

    strong_factors: list[str] = Field(
        default_factory=list,
    )

    weak_factors: list[str] = Field(
        default_factory=list,
    )

    contradictions: list[str] = Field(
        default_factory=list,
    )

    warnings: list[str] = Field(
        default_factory=list,
    )

    summary: str

    disclaimer: str = (
        "This analysis interprets supplied economic "
        "evidence. It does not predict the direction "
        "of a financial instrument and is not "
        "financial advice."
    )



class NFPTextAnalysisRequest(BaseModel):
    """
    Raw user-supplied NFP evidence.

    The evidence may contain copied economic
    release text, notes or news context.
    """

    evidence: str = Field(
        min_length=1,
        max_length=50000,
    )


class NFPExtractedEvidenceResponse(BaseModel):
    nfp_actual: float | None = None
    nfp_forecast: float | None = None
    nfp_previous: float | None = None
    nfp_revised_previous: float | None = None

    unemployment_actual: float | None = None
    unemployment_forecast: float | None = None
    unemployment_previous: float | None = None

    wage_mom_actual: float | None = None
    wage_mom_forecast: float | None = None
    wage_mom_previous: float | None = None

    wage_yoy_actual: float | None = None
    wage_yoy_forecast: float | None = None
    wage_yoy_previous: float | None = None

    adp_actual: float | None = None
    adp_forecast: float | None = None
    adp_previous: float | None = None

    jolts_actual: float | None = None
    jolts_forecast: float | None = None
    jolts_previous: float | None = None

    claims_actual: float | None = None
    claims_forecast: float | None = None
    claims_previous: float | None = None

    evidence_notes: list[str] = Field(
        default_factory=list,
    )

    uncertainties: list[str] = Field(
        default_factory=list,
    )


class NFPTextAnalysisResponse(
    NFPAnalysisResponse
):
    extracted_evidence: (
        NFPExtractedEvidenceResponse
    )


class MarketDirectionalBiasResponse(
    BaseModel
):
    market: str

    bias: Literal[
        "BULLISH",
        "BEARISH",
        "MIXED",
        "NEUTRAL",
    ]

    confidence: float = Field(
        ge=0,
        le=100,
    )

    explanation: str


class DirectionalBiasResponse(
    BaseModel
):
    overall_context: str

    markets: list[
        MarketDirectionalBiasResponse
    ] = Field(
        default_factory=list,
    )

    disclaimer: str


class NFPMultimodalAnalysisResponse(
    NFPTextAnalysisResponse
):
    directional_bias: (
        DirectionalBiasResponse
    )

    evidence_sources: list[str] = Field(
        default_factory=list,
    )



class GeneralMacroEvidenceItem(BaseModel):
    indicator: str
    actual: str | None = None
    forecast: str | None = None
    previous: str | None = None
    unit: str | None = None
    category: str | None = None
    relevance: Literal[
        "HIGH",
        "MEDIUM",
        "LOW",
        "UNKNOWN",
    ] = "UNKNOWN"
    interpretation: str = ""


class GeneralMacroEvidenceResponse(BaseModel):
    indicator: str
    actual: str | None = None
    forecast: str | None = None
    previous: str | None = None
    unit: str | None = None
    category: str | None = None
    relevance: Literal[
        "HIGH",
        "MEDIUM",
        "LOW",
        "UNKNOWN",
    ] = "UNKNOWN"
    interpretation: str = ""


class GeneralMacroAnalysisResponse(BaseModel):
    event: str
    currency: str | None = None

    classification: Literal[
        "STRONG",
        "POSITIVE",
        "MIXED",
        "WEAK",
        "INCONCLUSIVE",
    ]

    confidence: float = Field(
        ge=0,
        le=100,
    )

    usd_bias: Literal[
        "BULLISH",
        "BEARISH",
        "NEUTRAL",
        "MIXED",
    ]

    usd_bias_confidence: float = Field(
        ge=0,
        le=100,
    )

    summary: str

    positive_factors: list[str] = Field(
        default_factory=list,
    )

    negative_factors: list[str] = Field(
        default_factory=list,
    )

    contradictions: list[str] = Field(
        default_factory=list,
    )

    missing_information: list[str] = Field(
        default_factory=list,
    )

    extracted_indicators: list[
        GeneralMacroEvidenceResponse
    ] = Field(
        default_factory=list,
    )

    evidence_sources: list[str] = Field(
        default_factory=list,
    )

    warnings: list[str] = Field(
        default_factory=list,
    )

    disclaimer: str = (
        "This analysis interprets supplied economic "
        "evidence using AI. It is not financial advice "
        "and does not place or recommend trades."
    )


class GeneralMacroTextRequest(BaseModel):
    evidence: str = Field(
        min_length=1,
        max_length=50000,
    )
