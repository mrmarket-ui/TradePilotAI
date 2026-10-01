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
