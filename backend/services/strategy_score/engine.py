from services.strategy_score import StrategyScoreResult

from services.strategy_score.market import score_market
from services.strategy_score.session import score_session
from services.strategy_score.timeframe import score_timeframe
from services.strategy_score.entry import score_entry_rules
from services.strategy_score.confirmation import score_confirmations
from services.strategy_score.risk import score_risk
from services.strategy_score.psychology import score_psychology
from services.strategy_score.limits import score_limits

from services.strategy_score.verdict import (
    classify_verdict,
    build_recommendation,
)


def score_strategy(
    strategy,
    payload,
):
    components = [
        score_market(strategy, payload),
        score_session(strategy, payload),
        score_timeframe(strategy, payload),
        score_entry_rules(strategy, payload),
        score_confirmations(strategy, payload),
        score_risk(strategy, payload),
        score_psychology(strategy, payload),
        score_limits(strategy, payload),
    ]

    total = sum(c.earned for c in components)

    score = round(total,2)

    confidence = round(
        score,
        2,
    )

    strengths = []
    weaknesses = []

    for component in components:

        if component.passed:
            strengths.append(component.name)
        else:
            weaknesses.append(component.name)

    verdict = classify_verdict(score)

    recommendation = build_recommendation(
        score,
        weaknesses,
    )

    return StrategyScoreResult(
        overall_score=score,
        verdict=verdict,
        confidence=confidence,
        components=components,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendation=recommendation,
        metadata={
            "component_count": len(components)
        },
    )
