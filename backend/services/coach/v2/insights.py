"""
TradePilot AI Coach V2 Insights Engine.
"""

from __future__ import annotations

from typing import Any


def _to_dict(value: Any) -> dict:
    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    return {}


def generate_insights(analysis: Any) -> dict:

    data = _to_dict(analysis)

    risk = _to_dict(data.get("risk"))
    behavior = _to_dict(data.get("behavior"))
    psychology = _to_dict(data.get("psychology"))
    performance = _to_dict(data.get("performance"))
    consistency = _to_dict(data.get("consistency"))
    trader_dna = _to_dict(data.get("trader_dna"))

    strengths = trader_dna.get("strengths", [])
    weaknesses = trader_dna.get("weaknesses", [])

    biggest_strength = (
        strengths[0]
        if strengths
        else "Keep building good trading habits."
    )

    biggest_weakness = (
        weaknesses[0]
        if weaknesses
        else "No major weakness detected."
    )

    if behavior.get("revenge_trading"):
        weekly_focus = (
            "Avoid revenge trades after every losing position."
        )

    elif behavior.get("fomo_detected"):
        weekly_focus = (
            "Wait patiently for planned entries."
        )

    elif performance.get("profit_factor", 0) < 1:
        weekly_focus = (
            "Only take high-quality setups this week."
        )

    else:
        weekly_focus = (
            "Continue executing your trading plan consistently."
        )

    if risk.get("expectancy", 0) < 0:
        risk_level = "High"

    elif performance.get("profit_factor", 0) < 1.5:
        risk_level = "Medium"

    else:
        risk_level = "Low"

    score = consistency.get("score", {})

    if isinstance(score, dict):
        score = score.get("overall_score", 0)

    return {

        "headline":

            f"{trader_dna.get('profile','Developing Trader')}",

        "biggest_strength":

            biggest_strength,

        "biggest_weakness":

            biggest_weakness,

        "weekly_focus":

            weekly_focus,

        "risk_level":

            risk_level,

        "discipline":

            psychology.get(
                "discipline_score",
                0,
            ),

        "confidence":

            psychology.get(
                "confidence_score",
                0,
            ),

        "consistency_score":

            score,

        "overall_score":

            trader_dna.get(
                "overall_score",
                0,
            ),
    }
