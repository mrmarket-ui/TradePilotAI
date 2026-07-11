"""
TradePilot AI Coach V2 Goals Engine.
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


def generate_goals(analysis: Any) -> dict:

    data = _to_dict(analysis)

    risk = _to_dict(data.get("risk"))
    behavior = _to_dict(data.get("behavior"))
    performance = _to_dict(data.get("performance"))

    daily_goal = "Execute only trades that match your trading plan."

    if behavior.get("revenge_trading"):
        daily_goal = (
            "After every losing trade, wait at least 15 minutes before considering another entry."
        )

    elif behavior.get("fomo_detected"):
        daily_goal = (
            "Do not chase price. Wait for planned entry confirmation."
        )

    weekly_goal = "Review every trade before placing your next one."

    if performance.get("profit_factor", 0) < 1:
        weekly_goal = (
            "Take fewer trades and focus only on A+ setups."
        )

    next_20_trades = [
        "Follow your entry checklist before every trade.",
        "Risk the same amount on every position.",
        "Journal every completed trade.",
    ]

    if behavior.get("revenge_trading"):
        next_20_trades.insert(
            0,
            "Zero revenge trades.",
        )

    monthly_goal = (
        "Achieve a positive expectancy while maintaining disciplined execution."
    )

    if risk.get("expectancy", 0) >= 0:
        monthly_goal = (
            "Increase consistency without increasing risk."
        )

    return {
        "today": daily_goal,
        "this_week": weekly_goal,
        "next_20_trades": next_20_trades,
        "this_month": monthly_goal,
    }
