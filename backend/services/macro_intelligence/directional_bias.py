from dataclasses import dataclass, field

from .types import NFPAnalysisResult


@dataclass(slots=True)
class MarketDirectionalBias:
    market: str
    bias: str
    confidence: float
    explanation: str


@dataclass(slots=True)
class DirectionalBiasResult:
    overall_context: str

    markets: list[
        MarketDirectionalBias
    ] = field(
        default_factory=list
    )

    disclaimer: str = (
        "Directional bias is an interpretation "
        "of the supplied macroeconomic evidence. "
        "It is not a trade signal, does not "
        "guarantee market direction, and is not "
        "financial advice."
    )


def _base_direction(
    analysis: NFPAnalysisResult,
) -> str:
    if analysis.classification == "STRONG":
        return "POSITIVE"

    if analysis.classification == "WEAK":
        return "NEGATIVE"

    if analysis.contradictions:
        return "MIXED"

    return "NEUTRAL"


def _directional_confidence(
    analysis: NFPAnalysisResult,
) -> float:
    confidence = min(
        analysis.confidence,
        90.0,
    )

    if (
        analysis.classification
        == "INCONCLUSIVE"
    ):
        confidence = min(
            confidence,
            60.0,
        )

    return round(
        max(
            20.0,
            confidence,
        ),
        1,
    )


def analyze_directional_bias(
    analysis: NFPAnalysisResult,
) -> DirectionalBiasResult:
    """
    Convert the deterministic NFP release
    interpretation into a macro directional
    bias.

    This does NOT produce trading instructions.

    The bias reflects the common macroeconomic
    pressure associated with the supplied labour
    market evidence.

    Actual market price can behave differently
    because of positioning, expectations, other
    simultaneous releases, Federal Reserve
    expectations and liquidity conditions.
    """

    direction = _base_direction(
        analysis
    )

    confidence = (
        _directional_confidence(
            analysis
        )
    )

    if direction == "POSITIVE":
        usd_bias = "BULLISH"
        gold_bias = "BEARISH"
        treasury_bias = "BEARISH"

        usd_reason = (
            "The labour-market release is "
            "collectively stronger than "
            "expectations, which can support "
            "USD macro pressure."
        )

        gold_reason = (
            "A stronger labour-market release "
            "can support USD and rate "
            "expectations, creating bearish "
            "macro pressure for gold."
        )

        treasury_reason = (
            "Stronger labour data can support "
            "higher yield expectations, which "
            "creates bearish pressure on US "
            "Treasury prices."
        )

    elif direction == "NEGATIVE":
        usd_bias = "BEARISH"
        gold_bias = "BULLISH"
        treasury_bias = "BULLISH"

        usd_reason = (
            "The labour-market release is "
            "collectively weaker than "
            "expectations, which can create "
            "bearish USD macro pressure."
        )

        gold_reason = (
            "A weaker labour-market release "
            "can reduce USD and rate pressure, "
            "creating bullish macro pressure "
            "for gold."
        )

        treasury_reason = (
            "Weaker labour data can reduce "
            "yield expectations, creating "
            "bullish pressure on US Treasury "
            "prices."
        )

    elif direction == "MIXED":
        usd_bias = "MIXED"
        gold_bias = "MIXED"
        treasury_bias = "MIXED"

        common_reason = (
            "The release contains meaningful "
            "conflicting signals, so a reliable "
            "directional macro bias is not "
            "supported."
        )

        usd_reason = common_reason
        gold_reason = common_reason
        treasury_reason = common_reason

    else:
        usd_bias = "NEUTRAL"
        gold_bias = "NEUTRAL"
        treasury_bias = "NEUTRAL"

        common_reason = (
            "The available evidence does not "
            "produce a sufficiently strong "
            "directional macro signal."
        )

        usd_reason = common_reason
        gold_reason = common_reason
        treasury_reason = common_reason

    # Equity reaction to labour data is less
    # mechanically directional because stronger
    # growth can be positive while stronger rate
    # expectations can be negative.
    if direction in {
        "POSITIVE",
        "NEGATIVE",
        "MIXED",
    }:
        equity_bias = "MIXED"

        equity_reason = (
            "US equity reaction is context "
            "dependent. Labour-market strength "
            "or weakness can affect both growth "
            "expectations and Federal Reserve "
            "rate expectations in opposing ways."
        )
    else:
        equity_bias = "NEUTRAL"

        equity_reason = (
            "The supplied labour-market evidence "
            "does not support a strong equity "
            "macro bias."
        )

    equity_confidence = round(
        min(
            confidence,
            55.0,
        ),
        1,
    )

    if analysis.classification == "STRONG":
        context = (
            "The release has a strong positive "
            "labour-market surprise. Directional "
            "biases below describe the macro "
            "pressure normally associated with "
            "that evidence."
        )

    elif analysis.classification == "WEAK":
        context = (
            "The release has a strong negative "
            "labour-market surprise. Directional "
            "biases below describe the macro "
            "pressure normally associated with "
            "that evidence."
        )

    elif analysis.contradictions:
        context = (
            "The release contains conflicting "
            "economic signals, so directional "
            "confidence is intentionally limited."
        )

    else:
        context = (
            "The release is not sufficiently "
            "strong or weak to support a high "
            "confidence directional bias."
        )

    return DirectionalBiasResult(
        overall_context=context,
        markets=[
            MarketDirectionalBias(
                market="US Dollar",
                bias=usd_bias,
                confidence=confidence,
                explanation=usd_reason,
            ),
            MarketDirectionalBias(
                market="Gold",
                bias=gold_bias,
                confidence=confidence,
                explanation=gold_reason,
            ),
            MarketDirectionalBias(
                market="US Treasury Prices",
                bias=treasury_bias,
                confidence=confidence,
                explanation=treasury_reason,
            ),
            MarketDirectionalBias(
                market="US Equities",
                bias=equity_bias,
                confidence=equity_confidence,
                explanation=equity_reason,
            ),
        ],
    )
