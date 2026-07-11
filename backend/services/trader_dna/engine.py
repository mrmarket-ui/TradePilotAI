"""
TradePilot AI Trader DNA Engine.
"""

from services.trader_dna.classifier import classify_trader
from services.trader_dna.strengths import identify_strengths
from services.trader_dna.weaknesses import identify_weaknesses
from services.trader_dna.personality import identify_personality


def _consistency_value(consistency: dict) -> float:
    score = consistency.get("score", 50)

    if isinstance(score, dict):
        return float(score.get("overall_score", 50) or 50)

    return float(score or 50)


def analyze_trader_dna(
    statistics: dict,
    risk: dict,
    consistency: dict,
    psychology: dict,
    behavior: dict,
) -> dict:
    normalized_consistency = {
        **consistency,
        "score": _consistency_value(consistency),
    }

    profile = classify_trader(
        statistics,
        risk,
        normalized_consistency,
        psychology,
        behavior,
    )

    strengths = identify_strengths(
        statistics,
        risk,
        normalized_consistency,
        psychology,
        behavior,
    )

    weaknesses = identify_weaknesses(
        psychology,
        behavior,
    )

    personality = identify_personality(
        normalized_consistency,
        psychology,
        behavior,
    )

    score = round(
        (
            normalized_consistency["score"]
            + float(psychology.get("discipline_score", 50) or 50)
            + float(psychology.get("emotional_control", 50) or 50)
            + float(risk.get("risk_score", 50) or 50)
        )
        / 4,
        1,
    )

    return {
        "profile": profile,
        "overall_score": score,
        "personality": personality,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }
