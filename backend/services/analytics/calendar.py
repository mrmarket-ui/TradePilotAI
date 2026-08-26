from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Iterable


def _trade_date(trade) -> date | None:
    timestamp = (
        getattr(trade, "closed_at", None)
        or getattr(trade, "opened_at", None)
        or getattr(trade, "created_at", None)
    )

    if timestamp is None:
        return None

    return timestamp.date()


def build_trading_calendar(
    trades: Iterable,
) -> list[dict]:
    grouped = defaultdict(list)

    for trade in trades:
        trade_date = _trade_date(trade)

        if trade_date is None:
            continue

        grouped[trade_date].append(trade)

    result = []

    for trading_day, items in sorted(
        grouped.items(),
        key=lambda item: item[0],
    ):
        profits = [
            float(
                getattr(
                    trade,
                    "profit",
                    None,
                )
                or 0
            )
            for trade in items
        ]

        wins = sum(
            1
            for value in profits
            if value > 0
        )

        losses = sum(
            1
            for value in profits
            if value < 0
        )

        breakeven = sum(
            1
            for value in profits
            if value == 0
        )

        net_profit = sum(
            profits
        )

        result.append({
            "date":
                trading_day.isoformat(),

            "trades":
                len(items),

            "wins":
                wins,

            "losses":
                losses,

            "breakeven":
                breakeven,

            "net_profit":
                round(
                    net_profit,
                    2,
                ),

            "win_rate":
                round(
                    wins /
                    len(items) *
                    100,
                    2,
                )
                if items
                else 0.0,

            "result":
                (
                    "profit"
                    if net_profit > 0
                    else "loss"
                    if net_profit < 0
                    else "breakeven"
                ),
        })

    return result
