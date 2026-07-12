"""
TradePilot AI Chat Engine
Conversation-aware version
"""

from __future__ import annotations

import logging

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


def _fallback_reply(message: str, context: dict) -> str:

    performance = context.get("performance", {})
    behavior = context.get("behavior", {})
    trader = context.get("trader_dna", {})

    text = message.lower()

    if "lose" in text:

        answer = (
            f"Your current win rate is "
            f"{performance.get('win_rate',0)}% "
            f"with a profit factor of "
            f"{performance.get('profit_factor',0)}."
        )

        if behavior.get("revenge_trading"):
            answer += (
                " Revenge trading appears frequently."
            )

        answer += (
            " Focus on execution before increasing risk."
        )

        return answer

    if "dna" in text:

        return (
            f"Your Trader DNA profile is "
            f"{trader.get('profile','Unknown')}."
        )

    return (
        "I'm here to help you become a better trader."
    )


def generate_chat_reply(
    user_id: int,
    message: str,
    context: dict,
):

    add_message(
        user_id,
        "user",
        message,
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

            logger.exception(exc)

            answer = _fallback_reply(
                message,
                context,
            )

    else:

        answer = _fallback_reply(
            message,
            context,
        )

    add_message(
        user_id,
        "assistant",
        answer,
    )

    return build_response(answer)
