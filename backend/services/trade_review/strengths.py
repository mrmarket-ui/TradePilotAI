"""
TradePilot AI Trade Review Strength Detector.
"""

from __future__ import annotations

from typing import Any


def identify_trade_strengths(
    trade: Any,
) -> list[str]:
    strengths = []

    profit = float(
        getattr(trade, "profit", 0) or 0
    )

    entry = getattr(trade, "entry", None)
    stop_loss = getattr(trade, "stop_loss", None)
    take_profit = getattr(trade, "take_profit", None)

    strategy = getattr(trade, "strategy", None)
    lot_size = getattr(trade, "lot_size", None)

    if stop_loss is not None:
        strengths.append("Used a defined stop loss")

    if take_profit is not None:
        strengths.append("Used a planned take-profit target")

    if strategy and str(strategy).strip().lower() != "unspecified":
        strengths.append("Recorded a clear trading strategy")

    if lot_size is not None:
        strengths.append("Recorded position size")

    if profit > 0:
        strengths.append("Closed the trade profitably")

    if (
        entry is not None
        and stop_loss is not None
        and take_profit is not None
    ):
        risk = abs(float(entry) - float(stop_loss))
        reward = abs(float(take_profit) - float(entry))

        if risk > 0 and reward / risk >= 2:
            strengths.append(
                "Planned a strong risk-to-reward ratio"
            )

    if not strengths:
        strengths.append(
            "Completed and recorded the trade for review"
        )

    return strengths
