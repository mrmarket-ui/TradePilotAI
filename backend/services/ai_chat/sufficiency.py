"""
TradePilot AI chat data-sufficiency rules.

With too few trades, the scores and flags in the chat context are not real
(they start from defaults, not from the trader's behaviour), so they are
withheld from both the language model and the local fallback replies.
"""

from __future__ import annotations

from typing import Any

from services.analysis.sufficiency import (
    MIN_TRADES_TRADER_DNA,
    NOT_ENOUGH_DATA,
)


def apply_data_sufficiency(
    context: dict[str, Any],
    trade_count: int,
) -> dict[str, Any]:
    if trade_count >= MIN_TRADES_TRADER_DNA:
        return context

    needed = MIN_TRADES_TRADER_DNA - trade_count

    honest: dict[str, Any] = {"trade_count": trade_count}

    if "recent_trades" in context:
        honest["recent_trades"] = context["recent_trades"]

    honest["trader_dna"] = {
        "profile": NOT_ENOUGH_DATA,
        "sufficient_data": False,
        "trades_needed": needed,
        "strengths": [],
        "weaknesses": [],
    }

    honest["data_status"] = {
        "sufficient_data": False,
        "trades_logged": trade_count,
        "trades_needed": needed,
        "note": (
            "Scores, behaviour flags, strengths, weaknesses and "
            "recommendations are withheld because there are too few "
            "trades to measure them reliably. Do not infer or estimate "
            "discipline, consistency, psychology or a trader profile."
        ),
    }

    return honest