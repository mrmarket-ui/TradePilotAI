"""
TradePilot AI Coach V2
Improvement Plan Engine
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


def generate_improvement_plan(
    analysis: Any,
) -> list[dict]:

    data = _to_dict(analysis)

    behavior = _to_dict(
        data.get("behavior")
    )

    risk = _to_dict(
        data.get("risk")
    )

    performance = _to_dict(
        data.get("performance")
    )

    plan = []

    # -----------------------------
    # Week 1
    # -----------------------------

    week1 = []

    if behavior.get("revenge_trading"):
        week1.append(
            "Eliminate revenge trading completely."
        )

    if behavior.get("fomo_detected"):
        week1.append(
            "Only enter trades after confirmation."
        )

    if not week1:
        week1.append(
            "Maintain your current trading discipline."
        )

    # -----------------------------
    # Week 2
    # -----------------------------

    week2 = []

    if risk.get("expectancy", 0) < 0:
        week2.append(
            "Review every losing trade and identify recurring mistakes."
        )

    if performance.get("profit_factor", 0) < 1:
        week2.append(
            "Trade fewer but higher-quality setups."
        )

    if not week2:
        week2.append(
            "Maintain consistent execution."
        )

    # -----------------------------
    # Week 3
    # -----------------------------

    week3 = [
        "Risk a fixed percentage on every trade.",
        "Review your journal at the end of every trading day."
    ]

    # -----------------------------
    # Week 4
    # -----------------------------

    week4 = [
        "Evaluate progress using TradePilot AI analytics.",
        "Adjust your trading plan only after reviewing at least 20 trades."
    ]

    plan.append({
        "week": 1,
        "title": "Control Your Emotions",
        "tasks": week1,
    })

    plan.append({
        "week": 2,
        "title": "Improve Execution",
        "tasks": week2,
    })

    plan.append({
        "week": 3,
        "title": "Build Consistency",
        "tasks": week3,
    })

    plan.append({
        "week": 4,
        "title": "Evaluate Progress",
        "tasks": week4,
    })

    return plan
