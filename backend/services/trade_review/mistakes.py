"""
TradePilot AI Trade Review Mistake Detector.
"""

from __future__ import annotations

from typing import Any


def identify_trade_mistakes(
    trade: Any,
) -> list[str]:
    mistakes = []

    profit = float(
        getattr(trade, "profit", 0) or 0
    )

    entry = getattr(trade, "entry", None)
    stop_loss = getattr(trade, "stop_loss", None)
    take_profit = getattr(trade, "take_profit", None)

    strategy = getattr(trade, "strategy", None)
    lot_size = getattr(trade, "lot_size", None)

    if stop_loss is None:
        mistakes.append(
            "No stop loss was recorded"
        )

    if take_profit is None:
        mistakes.append(
            "No take-profit target was recorded"
        )

    if not strategy or str(strategy).strip().lower() == "unspecified":
        mistakes.append(
            "The trading strategy was not labelled"
        )

    if lot_size is None:
        mistakes.append(
            "Position size was not recorded"
        )

    if (
        entry is not None
        and stop_loss is not None
        and take_profit is not None
    ):
        risk = abs(float(entry) - float(stop_loss))
        reward = abs(float(take_profit) - float(entry))

        if risk <= 0:
            mistakes.append(
                "The stop-loss distance is invalid"
            )
        elif reward / risk < 1:
            mistakes.append(
                "The planned reward was smaller than the risk"
            )

    if profit < 0:
        mistakes.append(
            "The trade closed at a loss"
        )

    return mistakes
