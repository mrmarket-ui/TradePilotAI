"""
TradePilot AI Chat Engine
Conversation-aware version with LLM fallback.
"""

from __future__ import annotations

import logging
from typing import Any

from services.ai_chat.formatter import build_response
from services.ai_chat.memory import (
    add_message,
    get_history,
)
from services.ai_chat.llm import (
    generate_llm_reply,
    is_llm_configured,
)


logger = logging.getLogger(__name__)


def _fallback_reply(
    message: str,
    context: dict[str, Any],
) -> str:
    text = message.lower().strip()

    data_status = context.get("data_status") or {}

    if data_status.get("sufficient_data") is False and not any(
        keyword in text
        for keyword in ("recent", "last 20", "review my trades")
    ):
        if data_status.get("reason") == "missing_times":
            return (
                "I have your trades, but too few of them have open and close "
                "times for a reliable behaviour read. Add times to "
                f"{data_status.get('trades_needed', 0)} more trades and I can "
                "assess your discipline, consistency and Trader DNA. You can "
                "still ask me to review your recent trades."
            )

        return (
            "I don't have enough trades logged to give you a reliable "
            f"read yet (you have {data_status.get('trades_logged', 0)}). "
            f"Log {data_status.get('trades_needed', 0)} more and I can "
            "assess your discipline, consistency and Trader DNA. You can "
            "still ask me to review your recent trades."
        )

    risk = context.get("risk", {})
    performance = context.get("performance", {})
    behavior = context.get("behavior", {})
    psychology = context.get("psychology", {})
    consistency = context.get("consistency", {})
    trader_dna = context.get("trader_dna", {})
    recommendations = context.get(
        "recommendations",
        [],
    )
    recent_trades = context.get(
        "recent_trades",
        [],
    )

    if any(
        keyword in text
        for keyword in (
            "lose",
            "losing",
            "loss",
            "losses",
            "unprofitable",
        )
    ):
        answer = (
            f"Your current win rate is "
            f"{performance.get('win_rate', 0)}% "
            f"with a profit factor of "
            f"{performance.get('profit_factor', 0)}."
        )

        if float(risk.get("expectancy", 0) or 0) < 0:
            answer += (
                " Your expectancy is negative, which means your "
                "current execution is not producing a sustainable edge."
            )

        if behavior.get("revenge_trading"):
            answer += (
                " Revenge trading is present and may be increasing "
                "your losses after unsuccessful trades."
            )

        answer += (
            " For your next 20 trades, focus on higher-quality setups, "
            "fixed risk and zero emotional re-entries."
        )

        return answer

    if any(
        keyword in text
        for keyword in (
            "psychology",
            "emotion",
            "confidence",
            "discipline",
        )
    ):
        return (
            f"Your discipline score is "
            f"{psychology.get('discipline_score', 0)}, "
            f"your confidence score is "
            f"{psychology.get('confidence_score', 0)}, "
            f"and your emotional-control score is "
            f"{psychology.get('emotional_control', 0)}. "
            "Focus first on the behaviour causing the greatest "
            "damage to your execution."
        )

    if any(
        keyword in text
        for keyword in (
            "dna",
            "profile",
            "type of trader",
        )
    ):
        strengths = trader_dna.get(
            "strengths",
            [],
        )
        weaknesses = trader_dna.get(
            "weaknesses",
            [],
        )

        strength = (
            strengths[0]
            if strengths
            else "No reliable strength identified yet"
        )

        weakness = (
            weaknesses[0]
            if weaknesses
            else "No major weakness identified"
        )

        return (
            f"Your Trader DNA profile is "
            f"{trader_dna.get('profile', 'Developing Trader')}. "
            f"Your strongest current quality is {strength}. "
            f"Your main weakness is {weakness}."
        )

    if any(
        keyword in text
        for keyword in (
            "recommend",
            "focus",
            "improve",
            "priority",
        )
    ):
        if recommendations:
            top = recommendations[0]

            return (
                f"Your highest-priority focus is "
                f"{top.get('title', 'Improve execution')}. "
                f"{top.get('message', '')}"
            )

        return (
            "Continue following your trading plan and collect more "
            "labelled trade data for stronger recommendations."
        )

    if any(
        keyword in text
        for keyword in (
            "recent",
            "last 20",
            "review my trades",
        )
    ):
        wins = sum(
            1
            for trade in recent_trades
            if float(trade.get("profit", 0) or 0) > 0
        )

        losses = sum(
            1
            for trade in recent_trades
            if float(trade.get("profit", 0) or 0) < 0
        )

        net_profit = sum(
            float(trade.get("profit", 0) or 0)
            for trade in recent_trades
        )

        return (
            f"I reviewed {len(recent_trades)} recent trades: "
            f"{wins} wins, {losses} losses and a net result of "
            f"{net_profit:.2f}. Review the losing trades for repeated "
            "entry, risk and emotional-execution mistakes."
        )

    score = consistency.get("score", {})

    if isinstance(score, dict):
        score = score.get(
            "overall_score",
            0,
        )

    if trader_dna.get("sufficient_data", True) is False:
        needed = int(trader_dna.get("trades_needed") or 0)
        more = (
            f"{needed} more completed trades"
            if needed > 0
            else "more completed trades"
        )
        return (
            "I don't have enough completed trades to profile you yet. "
            f"Log {more} and I can give you a real Trader DNA and "
            "consistency read. You can still ask about a specific trade."
        )
    return (
        f"You are currently classified as a "
        f"{trader_dna.get('profile', 'Developing Trader')} "
        f"with a consistency score of {score}. "
        "Ask about your losses, psychology, Trader DNA, recent trades "
        "or highest-priority recommendation."
    )


def generate_chat_reply(
    user_id: int,
    message: str,
    context: dict[str, Any],
) -> dict:
    add_message(
        user_id=user_id,
        role="user",
        content=message,
    )

    history = get_history(user_id)

    if is_llm_configured():
        try:
            answer = generate_llm_reply(
                message=message,
                context={
                    **context,
                    "conversation": history,
                },
            )

        except Exception as exc:
            logger.warning(
                "LLM unavailable; using local fallback: %s",
                exc,
            )

            answer = _fallback_reply(
                message=message,
                context=context,
            )
    else:
        answer = _fallback_reply(
            message=message,
            context=context,
        )

    add_message(
        user_id=user_id,
        role="assistant",
        content=answer,
    )

    return build_response(answer)
