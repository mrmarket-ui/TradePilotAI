from __future__ import annotations

from math import isfinite

from services.macro_intelligence.types import (
    NFPAnalysisResult,
    NFPInput,
    ScoreComponent,
)


STRONG_THRESHOLD = 20.0
WEAK_THRESHOLD = -20.0


def _clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    return max(
        minimum,
        min(maximum, value),
    )


def _valid_number(
    value: float | None,
) -> bool:
    return (
        value is not None
        and isfinite(value)
    )


def _relative_surprise(
    actual: float,
    forecast: float,
) -> float:
    """
    Difference relative to the size of the forecast.

    Example:
        actual   = 240
        forecast = 200

        surprise = +20%
    """

    denominator = max(
        abs(forecast),
        1.0,
    )

    return (
        actual - forecast
    ) / denominator


def _headline_component(
    data: NFPInput,
) -> ScoreComponent:
    if not (
        _valid_number(data.nfp_actual)
        and _valid_number(data.nfp_forecast)
    ):
        return ScoreComponent(
            name="Headline payrolls",
            score=0.0,
            weight=35.0,
            explanation=(
                "Actual and forecast payroll figures "
                "were not both supplied."
            ),
            available=False,
        )

    actual = float(data.nfp_actual)
    forecast = float(data.nfp_forecast)

    surprise = _relative_surprise(
        actual,
        forecast,
    )

    score = _clamp(
        surprise / 0.25 * 35.0,
        -35.0,
        35.0,
    )

    difference = actual - forecast

    if difference > 0:
        explanation = (
            f"NFP beat forecast by {difference:.1f}K "
            f"({surprise * 100:.1f}% surprise)."
        )
    elif difference < 0:
        explanation = (
            f"NFP missed forecast by "
            f"{abs(difference):.1f}K "
            f"({surprise * 100:.1f}% surprise)."
        )
    else:
        explanation = (
            "NFP matched the market forecast."
        )

    return ScoreComponent(
        name="Headline payrolls",
        score=score,
        weight=35.0,
        explanation=explanation,
    )


def _unemployment_component(
    data: NFPInput,
) -> ScoreComponent:
    if not (
        _valid_number(
            data.unemployment_actual
        )
        and _valid_number(
            data.unemployment_forecast
        )
    ):
        return ScoreComponent(
            name="Unemployment rate",
            score=0.0,
            weight=20.0,
            explanation=(
                "Actual and forecast unemployment "
                "rates were not both supplied."
            ),
            available=False,
        )

    actual = float(
        data.unemployment_actual
    )

    forecast = float(
        data.unemployment_forecast
    )

    # Lower unemployment than forecast is stronger.
    difference = forecast - actual

    score = _clamp(
        difference / 0.3 * 20.0,
        -20.0,
        20.0,
    )

    if actual < forecast:
        explanation = (
            f"Unemployment was {actual:.2f}% "
            f"versus {forecast:.2f}% forecast, "
            "supporting a stronger labour release."
        )
    elif actual > forecast:
        explanation = (
            f"Unemployment was {actual:.2f}% "
            f"versus {forecast:.2f}% forecast, "
            "weakening the labour release."
        )
    else:
        explanation = (
            "Unemployment matched forecast."
        )

    return ScoreComponent(
        name="Unemployment rate",
        score=score,
        weight=20.0,
        explanation=explanation,
    )


def _wage_component(
    actual: float | None,
    forecast: float | None,
    *,
    label: str,
    weight: float,
) -> ScoreComponent:
    if not (
        _valid_number(actual)
        and _valid_number(forecast)
    ):
        return ScoreComponent(
            name=label,
            score=0.0,
            weight=weight,
            explanation=(
                f"{label} actual and forecast "
                "were not both supplied."
            ),
            available=False,
        )

    actual_value = float(actual)
    forecast_value = float(forecast)

    difference = (
        actual_value - forecast_value
    )

    # A 0.2 percentage-point wage surprise is
    # treated as a large surprise for this model.
    score = _clamp(
        difference / 0.2 * weight,
        -weight,
        weight,
    )

    if difference > 0:
        explanation = (
            f"{label} beat forecast: "
            f"{actual_value:.2f}% vs "
            f"{forecast_value:.2f}%."
        )
    elif difference < 0:
        explanation = (
            f"{label} missed forecast: "
            f"{actual_value:.2f}% vs "
            f"{forecast_value:.2f}%."
        )
    else:
        explanation = (
            f"{label} matched forecast."
        )

    return ScoreComponent(
        name=label,
        score=score,
        weight=weight,
        explanation=explanation,
    )


def _revision_component(
    data: NFPInput,
) -> ScoreComponent:
    if not (
        _valid_number(data.nfp_previous)
        and _valid_number(
            data.nfp_revised_previous
        )
    ):
        return ScoreComponent(
            name="Previous payroll revision",
            score=0.0,
            weight=15.0,
            explanation=(
                "A previous and revised payroll "
                "figure were not both supplied."
            ),
            available=False,
        )

    previous = float(data.nfp_previous)
    revised = float(
        data.nfp_revised_previous
    )

    difference = revised - previous

    # 50K revision receives the full revision
    # component weight.
    score = _clamp(
        difference / 50.0 * 15.0,
        -15.0,
        15.0,
    )

    if difference > 0:
        explanation = (
            f"Previous NFP was revised upward "
            f"by {difference:.1f}K."
        )
    elif difference < 0:
        explanation = (
            f"Previous NFP was revised downward "
            f"by {abs(difference):.1f}K."
        )
    else:
        explanation = (
            "Previous NFP was not revised."
        )

    return ScoreComponent(
        name="Previous payroll revision",
        score=score,
        weight=15.0,
        explanation=explanation,
    )


def _detect_contradictions(
    components: list[ScoreComponent],
) -> list[str]:
    available = [
        component
        for component in components
        if component.available
        and abs(component.score) >= 2.0
    ]

    positive = [
        component
        for component in available
        if component.score > 0
    ]

    negative = [
        component
        for component in available
        if component.score < 0
    ]

    contradictions: list[str] = []

    if positive and negative:
        strong_positive = max(
            positive,
            key=lambda item: item.score,
        )

        strong_negative = min(
            negative,
            key=lambda item: item.score,
        )

        contradictions.append(
            (
                f"{strong_positive.name} points "
                "to strength while "
                f"{strong_negative.name} points "
                "to weakness."
            )
        )

    return contradictions


def _classification(
    score: float,
) -> str:
    if score >= STRONG_THRESHOLD:
        return "STRONG"

    if score <= WEAK_THRESHOLD:
        return "WEAK"

    return "INCONCLUSIVE"


def _confidence(
    score: float,
    components: list[ScoreComponent],
    contradictions: list[str],
) -> float:
    total_weight = sum(
        component.weight
        for component in components
    )

    available_weight = sum(
        component.weight
        for component in components
        if component.available
    )

    completeness = (
        available_weight / total_weight
        if total_weight
        else 0.0
    )

    magnitude = min(
        abs(score) / 70.0,
        1.0,
    )

    confidence = (
        30.0
        + completeness * 40.0
        + magnitude * 25.0
    )

    if contradictions:
        confidence -= 15.0

    return round(
        _clamp(
            confidence,
            20.0,
            95.0,
        ),
        1,
    )



def _adp_component(
    data: NFPInput,
) -> ScoreComponent:
    """
    ADP is supporting pre-NFP evidence, not the
    official payroll release.
    """

    if not (
        _valid_number(data.adp_actual)
        and _valid_number(data.adp_forecast)
    ):
        return ScoreComponent(
            name="ADP employment",
            score=0.0,
            weight=12.0,
            explanation=(
                "ADP actual and forecast were "
                "not both supplied."
            ),
            available=False,
        )

    actual = float(data.adp_actual)
    forecast = float(data.adp_forecast)

    surprise = _relative_surprise(
        actual,
        forecast,
    )

    score = _clamp(
        surprise / 0.25 * 12.0,
        -12.0,
        12.0,
    )

    difference = actual - forecast

    if difference > 0:
        explanation = (
            f"ADP employment beat forecast by "
            f"{difference:.1f}K."
        )
    elif difference < 0:
        explanation = (
            f"ADP employment missed forecast by "
            f"{abs(difference):.1f}K."
        )
    else:
        explanation = (
            "ADP employment matched forecast."
        )

    return ScoreComponent(
        name="ADP employment",
        score=score,
        weight=12.0,
        explanation=explanation,
    )


def _jolts_component(
    data: NFPInput,
) -> ScoreComponent:
    """
    Higher-than-expected job openings are treated
    as stronger labour-demand context.
    """

    if not (
        _valid_number(data.jolts_actual)
        and _valid_number(data.jolts_forecast)
    ):
        return ScoreComponent(
            name="JOLTS job openings",
            score=0.0,
            weight=8.0,
            explanation=(
                "JOLTS actual and forecast were "
                "not both supplied."
            ),
            available=False,
        )

    actual = float(data.jolts_actual)
    forecast = float(data.jolts_forecast)

    surprise = _relative_surprise(
        actual,
        forecast,
    )

    score = _clamp(
        surprise / 0.05 * 8.0,
        -8.0,
        8.0,
    )

    difference = actual - forecast

    if difference > 0:
        explanation = (
            "JOLTS job openings were "
            f"{difference:.2f}M above forecast."
        )
    elif difference < 0:
        explanation = (
            "JOLTS job openings were "
            f"{abs(difference):.2f}M below forecast."
        )
    else:
        explanation = (
            "JOLTS job openings matched forecast."
        )

    return ScoreComponent(
        name="JOLTS job openings",
        score=score,
        weight=8.0,
        explanation=explanation,
    )


def _claims_component(
    data: NFPInput,
) -> ScoreComponent:
    """
    Claims are inverse labour evidence:
    fewer claims than forecast are stronger;
    more claims than forecast are weaker.
    """

    if not (
        _valid_number(data.claims_actual)
        and _valid_number(data.claims_forecast)
    ):
        return ScoreComponent(
            name="Initial jobless claims",
            score=0.0,
            weight=10.0,
            explanation=(
                "Claims actual and forecast were "
                "not both supplied."
            ),
            available=False,
        )

    actual = float(data.claims_actual)
    forecast = float(data.claims_forecast)

    denominator = max(
        abs(forecast),
        1.0,
    )

    inverse_surprise = (
        forecast - actual
    ) / denominator

    score = _clamp(
        inverse_surprise / 0.10 * 10.0,
        -10.0,
        10.0,
    )

    difference = actual - forecast

    if difference < 0:
        explanation = (
            "Initial jobless claims were "
            f"{abs(difference):.1f}K below forecast, "
            "a firmer labour signal."
        )
    elif difference > 0:
        explanation = (
            "Initial jobless claims were "
            f"{difference:.1f}K above forecast, "
            "a softer labour signal."
        )
    else:
        explanation = (
            "Initial jobless claims matched forecast."
        )

    return ScoreComponent(
        name="Initial jobless claims",
        score=score,
        weight=10.0,
        explanation=explanation,
    )


def _has_official_release_evidence(
    data: NFPInput,
) -> bool:
    pairs = (
        (
            data.nfp_actual,
            data.nfp_forecast,
        ),
        (
            data.unemployment_actual,
            data.unemployment_forecast,
        ),
        (
            data.wage_mom_actual,
            data.wage_mom_forecast,
        ),
        (
            data.wage_yoy_actual,
            data.wage_yoy_forecast,
        ),
    )

    return any(
        _valid_number(actual)
        and _valid_number(forecast)
        for actual, forecast in pairs
    )


def _has_pre_nfp_evidence(
    data: NFPInput,
) -> bool:
    pairs = (
        (
            data.adp_actual,
            data.adp_forecast,
        ),
        (
            data.jolts_actual,
            data.jolts_forecast,
        ),
        (
            data.claims_actual,
            data.claims_forecast,
        ),
    )

    return any(
        _valid_number(actual)
        and _valid_number(forecast)
        for actual, forecast in pairs
    )


def analyze_nfp(
    data: NFPInput,
) -> NFPAnalysisResult:
    """
    Deterministic TradePilot AI NFP analysis.

    Positive score:
        stronger-than-expected labour release

    Negative score:
        weaker-than-expected labour release

    This function does NOT predict asset direction.
    """

    official_release = (
        _has_official_release_evidence(data)
    )

    pre_nfp = (
        _has_pre_nfp_evidence(data)
    )

    components = [
        _headline_component(data),
        _unemployment_component(data),
        _wage_component(
            data.wage_mom_actual,
            data.wage_mom_forecast,
            label="Average hourly earnings MoM",
            weight=15.0,
        ),
        _wage_component(
            data.wage_yoy_actual,
            data.wage_yoy_forecast,
            label="Average hourly earnings YoY",
            weight=15.0,
        ),
        _revision_component(data),
        _adp_component(data),
        _jolts_component(data),
        _claims_component(data),
    ]

    raw_score = sum(
        component.score
        for component in components
    )

    score = round(
        _clamp(
            raw_score,
            -100.0,
            100.0,
        ),
        1,
    )

    classification = _classification(
        score
    )

    contradictions = (
        _detect_contradictions(
            components
        )
    )

    confidence = _confidence(
        score,
        components,
        contradictions,
    )

    strong_factors = [
        component.explanation
        for component in components
        if component.available
        and component.score > 1.0
    ]

    weak_factors = [
        component.explanation
        for component in components
        if component.available
        and component.score < -1.0
    ]

    warnings: list[str] = []

    unavailable = [
        component.name
        for component in components
        if not component.available
    ]

    if unavailable:
        warnings.append(
            "Missing evidence: "
            + ", ".join(unavailable)
            + "."
        )

    if contradictions:
        warnings.append(
            "The release contains conflicting "
            "signals. Confidence was reduced."
        )

    if (
        pre_nfp
        and not official_release
    ):
        if classification == "STRONG":
            summary = (
                "Pre-NFP labour indicators are "
                "collectively stronger than market "
                "expectations. The official NFP "
                "release has not been supplied."
            )
        elif classification == "WEAK":
            summary = (
                "Pre-NFP labour indicators are "
                "collectively weaker than market "
                "expectations. The official NFP "
                "release has not been supplied."
            )
        else:
            summary = (
                "Pre-NFP labour indicators provide "
                "mixed or modest labour-market "
                "context. The official NFP release "
                "has not been supplied."
            )

        warnings.append(
            "Pre-release context only: ADP, JOLTS "
            "and jobless claims can inform labour "
            "context but do not determine the "
            "official NFP outcome."
        )

    elif classification == "STRONG":
        summary = (
            "The supplied NFP evidence is "
            "collectively stronger than market "
            "expectations."
        )
    elif classification == "WEAK":
        summary = (
            "The supplied NFP evidence is "
            "collectively weaker than market "
            "expectations."
        )
    else:
        summary = (
            "The supplied NFP evidence does not "
            "support a sufficiently strong "
            "strong-or-weak classification."
        )

    return NFPAnalysisResult(
        event="US Non-Farm Payrolls",
        classification=classification,
        score=score,
        confidence=confidence,
        components=components,
        strong_factors=strong_factors,
        weak_factors=weak_factors,
        warnings=warnings,
        contradictions=contradictions,
        summary=summary,
    )

