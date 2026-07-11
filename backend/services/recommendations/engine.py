from __future__ import annotations

from services.recommendations.priority import sort_recommendations
from services.recommendations.risk_rules import generate_risk_recommendations
from services.recommendations.behavior_rules import generate_behavior_recommendations
from services.recommendations.psychology_rules import generate_psychology_recommendations
from services.recommendations.consistency_rules import generate_consistency_recommendations
from services.recommendations.strategy_rules import generate_strategy_recommendations
from services.recommendations.performance_rules import generate_performance_recommendations


def _deduplicate(recommendations: list[dict]) -> list[dict]:
    """
    Remove recommendations with duplicate titles/messages while
    preserving the first, highest-priority occurrence.
    """

    unique = []
    seen = set()

    for item in recommendations:
        key = (
            item.get("title", "").strip().lower(),
            item.get("message", "").strip().lower(),
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

    return unique


def generate_recommendations(
    risk: dict,
    behavior: dict,
    psychology: dict,
    consistency: dict,
    strategies: dict,
    performance: dict,
) -> list[dict]:
    recommendations = []

    recommendations.extend(
        generate_risk_recommendations(risk)
    )
    recommendations.extend(
        generate_behavior_recommendations(behavior)
    )
    recommendations.extend(
        generate_psychology_recommendations(psychology)
    )
    recommendations.extend(
        generate_consistency_recommendations(consistency)
    )
    recommendations.extend(
        generate_strategy_recommendations(strategies)
    )
    recommendations.extend(
        generate_performance_recommendations(performance)
    )

    recommendations = sort_recommendations(
        recommendations
    )

    return _deduplicate(recommendations)
