"""
TradePilot AI consistency score.

A 0-100 measure of how repeatable and controlled a trader's process is.

Every component comes from a real measurement. The previous version read
psychology["score"] and behavior["score"], keys that never exist, so 20% of
the score was always the constant 50, and it counted win rate twice (as
"win rate" and again as "consistency").

Weights live in one table so they are easy to tune. Components whose input
is missing are left out and the remaining weights are rescaled, so a missing
measurement never pulls the score toward an invented value.
"""

from __future__ import annotations

import math

from services.analysis.sufficiency import MIN_TRADES_TRADER_DNA

WEIGHTS = {
    "discipline": 25,
    "emotional_control": 15,
    "profitability": 20,
    "win_rate": 15,
    "risk_recovery": 15,
    "improvement": 10,
}

TREND_SCORES = {
    "Improving": 100,
    "Mixed": 60,
    "Declining": 20,
}


def _clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def _number(value):
    """Return a float, or None for missing or unusable values."""

    if value is None or isinstance(value, bool):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if math.isnan(number):
        return None

    return number


def get_grade(score):

    if score >= 90:
        return "A+"

    if score >= 80:
        return "A"

    if score >= 70:
        return "B"

    if score >= 60:
        return "C"

    if score >= 50:
        return "D"

    return "F"


def insufficient_consistency(trade_count: int) -> dict:
    # overall_score stays numeric on purpose: older coach code compares it
    # with "<" and would fail on None. Display layers hide it when
    # sufficient_data is False.
    return {
        "overall_score": 0.0,
        "grade": None,
        "breakdown": {},
        "weights_used": {},
        "sufficient_data": False,
        "trades_needed": max(0, MIN_TRADES_TRADER_DNA - int(trade_count or 0)),
    }


def calculate_consistency_score(

    statistics,
    risk,
    psychology,
    behavior,
    improvement,
    trade_count=None,

):
    # "behavior" is accepted for compatibility. Its flags already feed the
    # discipline and emotional-control scores, so counting them again here
    # would double-count them.

    if trade_count is not None and trade_count < MIN_TRADES_TRADER_DNA:
        return insufficient_consistency(trade_count)

    statistics = statistics or {}
    risk = risk or {}
    psychology = psychology or {}

    components = {}

    discipline = _number(psychology.get("discipline_score"))
    if discipline is not None:
        components["discipline"] = _clamp(discipline)

    emotional = _number(psychology.get("emotional_control"))
    if emotional is not None:
        components["emotional_control"] = _clamp(emotional)

    profit_factor = _number(statistics.get("profit_factor"))
    if profit_factor is not None:
        components["profitability"] = _clamp(profit_factor * 50)

    win_rate = _number(statistics.get("win_rate"))
    if win_rate is not None:
        components["win_rate"] = _clamp(win_rate)

    recovery = _number(risk.get("recovery_factor"))
    if recovery is not None:
        components["risk_recovery"] = _clamp(recovery * 20)

    if improvement in TREND_SCORES:
        components["improvement"] = TREND_SCORES[improvement]

    weights_used = {
        name: WEIGHTS[name]
        for name in components
    }

    total_weight = sum(weights_used.values())

    if total_weight == 0:
        return insufficient_consistency(trade_count or 0)

    score = sum(
        components[name] * weights_used[name]
        for name in components
    ) / total_weight

    return {

        "overall_score": round(score, 2),

        "grade": get_grade(score),

        "breakdown": {
            name: round(value, 2)
            for name, value in components.items()
        },

        "weights_used": weights_used,

        "sufficient_data": True,

        "trades_needed": 0,

    }