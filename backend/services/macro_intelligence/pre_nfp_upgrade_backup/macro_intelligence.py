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

