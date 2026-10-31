"""
TradePilot AI chat data-sufficiency rules.

With too few trades, or too few trades with open and close times, the scores
and flags in the chat context are not real (they start from defaults, not from
the trader's behaviour), so they are withheld from both the language model and
the local fallback replies.
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
    trader_dna = context.get("trader_dna")

    locked_by_times = (
        isinstance(trader_dna, dict)
        and trader_dna.get("sufficient_data") is False
    )

    if trade_count >= MIN_TRADES_TRADER_DNA and not locked_by_times:
        return context

    few_trades = trade_count < MIN_TRADES_TRADER_DNA

    if few_trades:
        needed = MIN_TRADES_TRADER_DNA - trade_count
        reason = "few_trades"
        note = (
            "Scores, behaviour flags, strengths, weaknesses and "
            "recommendations are withheld because there are too few "
            "trades to measure them reliably. Do not infer or estimate "
            "discipline, consistency, psychology or a trader profile."
        )
    else:
        needed = int(trader_dna.get("trades_needed") or 0)
        reason = "missing_times"
        note = (
            "Scores, behaviour flags, strengths, weaknesses and "
            "recommendations are withheld because too few trades have "
            "open and close times to measure behaviour reliably. Tell the "
            "trader to add times to more trades. Do not infer or estimate "
            "discipline, consistency, psychology or a trader profile."
        )

    honest: dict[str, Any] = {"trade_count": trade_count}

    if "recent_trades" in context:
        honest["recent_trades"] = context["recent_trades"]

    honest["trader_dna"] = {
        "profile": NOT_ENOUGH_DATA,
        "sufficient_data": False,
        "trades_needed": needed,
        "reason": reason,
        "strengths": [],
        "weaknesses": [],
    }

    honest["data_status"] = {
        "sufficient_data": False,
        "trades_logged": trade_count,
        "trades_needed": needed,
        "reason": reason,
        "note": note,
    }

    return honest