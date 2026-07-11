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


def _consistency_score(consistency: dict) -> float:
    score = consistency.get("score", 0)

    if isinstance(score, dict):
        return float(
            score.get("overall_score", 0) or 0
        )

    return float(score or 0)


def generate_scorecard(analysis: Any) -> dict:
    data = _to_dict(analysis)

    risk = _to_dict(data.get("risk"))
    psychology = _to_dict(data.get("psychology"))
    consistency = _to_dict(data.get("consistency"))
    trader_dna = _to_dict(data.get("trader_dna"))

    recovery_factor = float(
        risk.get("recovery_factor", 0) or 0
    )

    risk_score = max(
        0.0,
        min(100.0, recovery_factor * 20),
    )

    discipline = float(
        psychology.get("discipline_score", 0) or 0
    )

    emotional_control = float(
        psychology.get("emotional_control", 0) or 0
    )

    psychology_score = round(
        (discipline + emotional_control) / 2,
        2,
    )

    return {
        "overall": float(
            trader_dna.get("overall_score", 0) or 0
        ),
        "risk": round(risk_score, 2),
        "psychology": psychology_score,
        "discipline": discipline,
        "consistency": _consistency_score(consistency),
    }
