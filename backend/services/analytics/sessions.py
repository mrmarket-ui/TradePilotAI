from __future__ import annotations

from collections import defaultdict
from typing import Iterable


def detect_session(
    trade,
) -> str:
    opened_at = getattr(
        trade,
        "opened_at",
        None,
    )

    if opened_at is None:
        return "Unknown"

    hour = opened_at.hour

    if 0 <= hour < 7:
        return "Asia"

    if 7 <= hour < 12:
        return "London"

    if 12 <= hour < 16:
        return "London / New York"

    if 16 <= hour < 21:
        return "New York"

    return "After Hours"


def analyze_sessions(
    trades: Iterable,
) -> dict:
    groups = defaultdict(
        list
    )

    for trade in trades:
        session = (
            detect_session(
                trade
            )
        )

        groups[
            session
        ].append(
            trade
        )

    result = {}

    for session, items in groups.items():
        profits = [
            float(
                getattr(
                    item,
                    "profit",
                    None,
                )
                or 0
            )
            for item in items
        ]

        wins = sum(
            1
            for profit
            in profits
            if profit > 0
        )

        losses = sum(
            1
            for profit
            in profits
            if profit < 0
        )

        breakeven = sum(
            1
            for profit
            in profits
            if profit == 0
        )

        count = len(
            items
        )

        gross_profit = sum(
            profit
            for profit
            in profits
            if profit > 0
        )

        gross_loss = abs(
            sum(
                profit
                for profit
                in profits
                if profit < 0
            )
        )

        if gross_loss > 0:
            profit_factor = (
                gross_profit /
                gross_loss
            )

        elif gross_profit > 0:
            profit_factor = (
                gross_profit
            )

        else:
            profit_factor = 0.0

        result[session] = {
            "trades":
                count,

            "wins":
                wins,

            "losses":
                losses,

            "breakeven":
                breakeven,

            "win_rate":
                round(
                    wins /
                    count *
                    100,
                    2,
                )
                if count
                else 0.0,

            "net_profit":
                round(
                    sum(
                        profits
                    ),
                    2,
                ),

            "average_profit":
                round(
                    sum(profits) /
                    count,
                    2,
                )
                if count
                else 0.0,

            "profit_factor":
                round(
                    profit_factor,
                    2,
                ),
        }

    return result
