"""
TradePilot AI Trader DNA strength analysis.
"""


def identify_strengths(
    statistics: dict,
    risk: dict,
    consistency: dict,
    psychology: dict,
    behavior: dict,
) -> list[str]:
    strengths = []

    consistency_score = consistency.get("score", 0)

    if isinstance(consistency_score, dict):
        consistency_score = consistency_score.get(
            "overall_score",
            0,
        )

    if statistics.get("win_rate", 0) >= 60:
        strengths.append("High win rate")

    if risk.get("risk_score", 0) >= 80:
        strengths.append("Excellent risk management")

    if consistency_score >= 80:
        strengths.append("Highly consistent")

    if (
        psychology.get("discipline_score", 0) >= 80
        and not behavior.get("revenge_trading", False)
        and not behavior.get("fomo_detected", False)
    ):
        strengths.append("Excellent discipline")

    if (
        psychology.get("emotional_control", 0) >= 80
        and not behavior.get("revenge_trading", False)
        and not behavior.get("holding_losers_too_long", False)
    ):
        strengths.append("Strong emotional control")

    if behavior.get("position_size_discipline", False):
        strengths.append("Consistent position sizing")

    if (
        behavior.get("strategy_discipline", False)
        and not behavior.get("fomo_detected", False)
    ):
        strengths.append("Follows trading rules consistently")

    if (
        behavior.get("session_discipline", False)
        and not behavior.get("weekend_trading", False)
    ):
        strengths.append("Maintains session discipline")

    if not strengths:
        strengths.append("Shows commitment to improving")

    return strengths
