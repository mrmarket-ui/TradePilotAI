"""
TradePilot AI Trade Review Engine.
"""

from __future__ import annotations

from typing import Any

from services.trade_review.scorer import score_trade
from services.trade_review.strengths import (
    identify_trade_strengths,
)
from services.trade_review.mistakes import (
    identify_trade_mistakes,
)
from services.trade_review.lessons import (
    generate_trade_lesson,
)
from services.trade_review.missions import (
    generate_next_mission,
)


def review_trade(
    trade: Any,
) -> dict:
    score = score_trade(trade)

    strengths = identify_trade_strengths(
        trade
    )

    mistakes = identify_trade_mistakes(
        trade
    )

    lesson = generate_trade_lesson(
        mistakes
    )

    next_mission = generate_next_mission(
        mistakes
    )

    if score >= 85:
        summary = (
            "Strong trade execution with good planning "
            "and disciplined risk structure."
        )
    elif score >= 70:
        summary = (
            "Solid trade with some execution areas that "
            "can still be improved."
        )
    elif score >= 50:
        summary = (
            "The trade showed partial planning, but several "
            "important execution details need attention."
        )
    else:
        summary = (
            "This trade requires significant improvement in "
            "planning, risk control and documentation."
        )

    return {
        "trade_score": score,
        "summary": summary,
        "strengths": strengths,
        "mistakes": mistakes,
        "lesson": lesson,
        "next_mission": next_mission,
    }
