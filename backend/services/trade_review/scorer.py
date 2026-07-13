"""
TradePilot AI Trade Review Scorer.
"""

from __future__ import annotations

from typing import Any


def score_trade(trade: Any) -> float:
    score = 100.0

    profit = float(
        getattr(trade, "profit", 0) or 0
    )

    entry = getattr(trade, "entry", None)
    stop_loss = getattr(trade, "stop_loss", None)
    take_profit = getattr(trade, "take_profit", None)

    opened_at = getattr(trade, "opened_at", None)
    closed_at = getattr(trade, "closed_at", None)

    strategy = getattr(trade, "strategy", None)
    lot_size = getattr(trade, "lot_size", None)

    if entry is None:
        score -= 10

    if stop_loss is None:
        score -= 20

    if take_profit is None:
        score -= 10

    if opened_at is None or closed_at is None:
        score -= 10

    if not strategy or str(strategy).strip().lower() == "unspecified":
        score -= 10

    if lot_size is None:
        score -= 5

    if profit < 0:
        score -= 15

    if (
        entry is not None
        and stop_loss is not None
        and take_profit is not None
    ):
        risk = abs(float(entry) - float(stop_loss))
        reward = abs(float(take_profit) - float(entry))

        if risk <= 0:
            score -= 15
        else:
            rr = reward / risk

            if rr < 1:
                score -= 20
            elif rr < 1.5:
                score -= 10
            elif rr >= 2:
                score += 5

    return round(
        max(0.0, min(100.0, score)),
        1,
    )
