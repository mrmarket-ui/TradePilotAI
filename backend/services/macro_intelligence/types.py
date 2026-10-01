from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class NFPInput:
    """
    Structured evidence for a US Non-Farm Payrolls release.
    """

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


    # Pre-NFP labour-market indicators.
    # Payroll values are expressed in thousands.
    adp_actual: float | None = None
    adp_forecast: float | None = None
    adp_previous: float | None = None

    # JOLTS job openings are expressed in millions.
    jolts_actual: float | None = None
    jolts_forecast: float | None = None
    jolts_previous: float | None = None

    # Initial unemployment claims are expressed
    # in thousands.
    claims_actual: float | None = None
    claims_forecast: float | None = None
    claims_previous: float | None = None


@dataclass(slots=True)
class ScoreComponent:
    name: str
    score: float
    weight: float
    explanation: str
    available: bool = True


@dataclass(slots=True)
class NFPAnalysisResult:
    event: str
    classification: str
    score: float
    confidence: float

    components: list[ScoreComponent] = field(
        default_factory=list
    )

    strong_factors: list[str] = field(
        default_factory=list
    )

    weak_factors: list[str] = field(
        default_factory=list
    )

    contradictions: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    summary: str = ""
