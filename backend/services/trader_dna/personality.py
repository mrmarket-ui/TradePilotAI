"""
TradePilot AI trader personality engine.
"""


def identify_personality(
    consistency: dict,
    psychology: dict,
    behavior: dict,
) -> list[str]:
    traits = []

    consistency_score = consistency.get("score", 0)

    if isinstance(consistency_score, dict):
        consistency_score = consistency_score.get(
            "overall_score",
            0,
        )

    emotional_issue = (
        behavior.get("revenge_trading", False)
        or behavior.get("fomo_detected", False)
        or psychology.get("stress_score", 0) > 70
    )

    if consistency_score >= 80:
        traits.append("Consistent")

    if (
        psychology.get("discipline_score", 0) >= 80
        and not behavior.get("revenge_trading", False)
    ):
        traits.append("Disciplined")

    if (
        psychology.get("emotional_control", 0) >= 80
        and not emotional_issue
    ):
        traits.append("Calm")

    if (
        psychology.get("confidence_score", 0) >= 80
        and not behavior.get("fomo_detected", False)
    ):
        traits.append("Confident")

    if (
        behavior.get("strategy_discipline", False)
        and not emotional_issue
    ):
        traits.append("Methodical")

    if (
        behavior.get("session_discipline", False)
        and not behavior.get("fomo_detected", False)
    ):
        traits.append("Patient")

    if behavior.get("revenge_trading", False):
        traits.append("Emotionally Reactive")

    if behavior.get("fomo_detected", False):
        traits.append("Opportunity Driven")

    if not traits:
        traits.append("Developing")

    return list(dict.fromkeys(traits))
