"""
TradePilot AI Coach V2 summary engine.

Creates a concise executive coaching summary from
the trader's unified analysis.
"""

from __future__ import annotations

from typing import Any


def _to_dict(value: Any) -> dict:
    """
    Convert Pydantic models or dictionaries into a dictionary.
    """

    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    return {}


def _score_value(consistency: dict) -> float:
    score = consistency.get("score", 0)

    if isinstance(score, dict):
        return float(
            score.get("overall_score", 0) or 0
        )

    return float(score or 0)


def generate_summary(analysis: Any) -> str:
    """
    Generate a personalized executive coaching summary.
    """

    data = _to_dict(analysis)

    risk = _to_dict(data.get("risk"))
    behavior = _to_dict(data.get("behavior"))
    psychology = _to_dict(data.get("psychology"))
    performance = _to_dict(data.get("performance"))
    consistency = _to_dict(data.get("consistency"))
    trader_dna = _to_dict(data.get("trader_dna"))

    profile = trader_dna.get(
        "profile",
        "Developing Trader",
    )

    win_rate = float(
        performance.get("win_rate", 0) or 0
    )

    profit_factor = float(
        performance.get("profit_factor", 0) or 0
    )

    expectancy = float(
        risk.get("expectancy", 0) or 0
    )

    consistency_score = _score_value(
        consistency
    )

    discipline = float(
        psychology.get("discipline_score", 0) or 0
    )

    issues = []

    if behavior.get("revenge_trading", False):
        issues.append("revenge trading")

    if behavior.get("fomo_detected", False):
        issues.append("FOMO entries")

    if behavior.get(
        "holding_losers_too_long",
        False,
    ):
        issues.append("holding losing trades too long")

    if behavior.get(
        "cutting_winners_too_early",
        False,
    ):
        issues.append("closing winning trades too early")

    if not behavior.get(
        "position_size_discipline",
        True,
    ):
        issues.append("inconsistent position sizing")

    if expectancy < 0:
        performance_message = (
            "Your current trading expectancy is negative, "
            "which means your recent execution is not yet producing "
            "a sustainable edge."
        )
    elif profit_factor < 1:
        performance_message = (
            "Your losses currently outweigh your gains, so protecting "
            "capital and improving setup quality should be your priority."
        )
    elif profit_factor >= 2 and win_rate >= 50:
        performance_message = (
            "Your results show a strong trading edge with healthy "
            "profitability."
        )
    else:
        performance_message = (
            "Your trading performance shows potential, but greater "
            "execution consistency is still required."
        )

    if consistency_score < 50:
        consistency_message = (
            "Your consistency score is currently low, so focus on "
            "repeating one clear process instead of changing your "
            "approach after individual results."
        )
    elif consistency_score < 75:
        consistency_message = (
            "Your consistency is developing, but your routine still "
            "needs stronger repetition."
        )
    else:
        consistency_message = (
            "Your execution is becoming consistent and should be "
            "protected through disciplined repetition."
        )

    if issues:
        issue_message = (
            "Your main behavioral obstacle is "
            + ", ".join(issues[:2])
            + "."
        )
    elif discipline >= 80:
        issue_message = (
            "Your behavioral discipline is currently a major strength."
        )
    else:
        issue_message = (
            "Your next improvement should come from clearer execution "
            "rules and stronger trade review habits."
        )

    return (
        f"You are currently classified as a {profile}. "
        f"{performance_message} "
        f"{consistency_message} "
        f"{issue_message}"
    )
