"""
TradePilot AI Chat Engine V1
"""

from services.ai_chat.formatter import build_response


def generate_chat_reply(
    message: str,
    context: dict,
):

    text = message.lower()

    performance = context.get(
        "performance",
        {},
    )

    behavior = context.get(
        "behavior",
        {},
    )

    psychology = context.get(
        "psychology",
        {},
    )

    trader_dna = context.get(
        "trader_dna",
        {},
    )

    # ---------------------------
    # Losing money
    # ---------------------------

    if (
        "lose" in text
        or "losing" in text
        or "loss" in text
    ):

        answer = (
            f"Your win rate is "
            f"{performance.get('win_rate',0)}% "
            f"with a profit factor of "
            f"{performance.get('profit_factor',0)}. "
        )

        if behavior.get(
            "revenge_trading"
        ):
            answer += (
                "Your analytics show revenge trading, "
                "which is one of your biggest contributors "
                "to poor performance. "
            )

        answer += (
            "Focus on improving execution before trying "
            "to increase profits."
        )

        return build_response(answer)

    # ---------------------------
    # Psychology
    # ---------------------------

    if "psychology" in text:

        answer = (
            f"Your discipline score is "
            f"{psychology.get('discipline_score',0)} "
            f"and your confidence score is "
            f"{psychology.get('confidence_score',0)}. "
            "Continue reinforcing disciplined execution."
        )

        return build_response(answer)

    # ---------------------------
    # Trader DNA
    # ---------------------------

    if "dna" in text or "profile" in text:

        answer = (
            "Your Trader DNA profile is "
            f"{trader_dna.get('profile','Unknown')}."
        )

        return build_response(answer)

    # ---------------------------
    # Default
    # ---------------------------

    return build_response(
        "I understand your question. As TradePilot AI grows I'll provide deeper personalised coaching using your trading history."
    )
