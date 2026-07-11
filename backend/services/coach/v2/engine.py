"""
TradePilot AI
AI Coach V2 Engine
"""

from __future__ import annotations

from typing import Any

from services.coach.v2.summary import generate_summary
from services.coach.v2.insights import generate_insights
from services.coach.v2.goals import generate_goals
from services.coach.v2.plan import generate_improvement_plan


def _motivation(analysis: Any) -> str:

    trader_dna = getattr(
        analysis,
        "trader_dna",
        {},
    )

    if hasattr(trader_dna, "model_dump"):
        trader_dna = trader_dna.model_dump()

    elif hasattr(trader_dna, "dict"):
        trader_dna = trader_dna.dict()

    score = trader_dna.get(
        "overall_score",
        0,
    )

    if score >= 80:
        return (
            "Excellent work. Stay disciplined and protect your edge."
        )

    if score >= 60:
        return (
            "You are improving. Consistency over the next 20 trades is your priority."
        )

    return (
        "Every professional trader started where you are today. Focus on execution, not profits."
    )


def _coach_message(analysis: Any) -> str:

    behavior = getattr(
        analysis,
        "behavior",
        {},
    )

    if hasattr(behavior, "model_dump"):
        behavior = behavior.model_dump()

    elif hasattr(behavior, "dict"):
        behavior = behavior.dict()

    if behavior.get("revenge_trading"):

        return (
            "Your biggest obstacle is revenge trading. "
            "For your next 20 trades your only objective is to eliminate emotional re-entries. "
            "Ignore profits and measure success purely by execution quality."
        )

    if behavior.get("fomo_detected"):

        return (
            "Your biggest obstacle is FOMO. Wait for confirmation and let the market come to you."
        )

    return (
        "Keep following your trading plan. Your next level comes from repeating disciplined execution."
    )


def generate_ai_coach(
    analysis: Any,
) -> dict:

    return {

        "summary":

            generate_summary(
                analysis,
            ),

        "insights":

            generate_insights(
                analysis,
            ),

        "goals":

            generate_goals(
                analysis,
            ),

        "improvement_plan":

            generate_improvement_plan(
                analysis,
            ),

        "motivation":

            _motivation(
                analysis,
            ),

        "coach_message":

            _coach_message(
                analysis,
            ),

    }
