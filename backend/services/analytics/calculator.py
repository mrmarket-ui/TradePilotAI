from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Iterable


def _profit(trade) -> float:
    return float(
        getattr(
            trade,
            "profit",
            None,
        )
        or 0
    )


def _closed_time(trade):
    return (
        getattr(
            trade,
            "closed_at",
            None,
        )
        or getattr(
            trade,
            "opened_at",
            None,
        )
        or getattr(
            trade,
            "created_at",
            None,
        )
    )


def _risk_amount(trade) -> float | None:
    entry = getattr(
        trade,
        "entry",
        None,
    )

    stop = getattr(
        trade,
        "stop_loss",
        None,
    )

    if entry is None or stop is None:
        return None

    risk = abs(
        float(entry) -
        float(stop)
    )

    if risk <= 0:
        return None

    return risk


def calculate_r_multiple(
    trade,
) -> float | None:
    entry = getattr(
        trade,
        "entry",
        None,
    )

    exit_price = getattr(
        trade,
        "exit_price",
        None,
    )

    direction = str(
        getattr(
            trade,
            "direction",
            "",
        )
        or ""
    ).upper()

    risk = _risk_amount(
        trade
    )

    if (
        entry is None
        or exit_price is None
        or risk is None
        or direction not in {
            "BUY",
            "SELL",
        }
    ):
        return None

    entry = float(entry)
    exit_price = float(
        exit_price
    )

    if direction == "BUY":
        reward = (
            exit_price -
            entry
        )
    else:
        reward = (
            entry -
            exit_price
        )

    return round(
        reward / risk,
        3,
    )


def calculate_expectancy(
    trades: Iterable,
) -> float:
    trades = list(
        trades
    )

    if not trades:
        return 0.0

    profits = [
        _profit(trade)
        for trade in trades
    ]

    return round(
        sum(profits) /
        len(profits),
        2,
    )


def calculate_streaks(
    trades: Iterable,
) -> dict:
    trades = sorted(
        list(trades),
        key=lambda trade:
            _closed_time(
                trade
            )
            or datetime.min,
    )

    current_win = 0
    current_loss = 0

    max_win = 0
    max_loss = 0

    for trade in trades:
        profit = _profit(
            trade
        )

        if profit > 0:
            current_win += 1
            current_loss = 0

            max_win = max(
                max_win,
                current_win,
            )

        elif profit < 0:
            current_loss += 1
            current_win = 0

            max_loss = max(
                max_loss,
                current_loss,
            )

        else:
            current_win = 0
            current_loss = 0

    return {
        "max_win_streak":
            max_win,

        "max_loss_streak":
            max_loss,
    }


def calculate_r_statistics(
    trades: Iterable,
) -> dict:
    values = []

    for trade in trades:
        value = (
            calculate_r_multiple(
                trade
            )
        )

        if value is not None:
            values.append(
                value
            )

    if not values:
        return {
            "trades_with_r": 0,
            "average_r": 0.0,
            "best_r": 0.0,
            "worst_r": 0.0,
            "total_r": 0.0,
        }

    return {
        "trades_with_r":
            len(values),

        "average_r":
            round(
                sum(values) /
                len(values),
                3,
            ),

        "best_r":
            round(
                max(values),
                3,
            ),

        "worst_r":
            round(
                min(values),
                3,
            ),

        "total_r":
            round(
                sum(values),
                3,
            ),
    }


def group_performance(
    trades: Iterable,
    field: str,
) -> dict:
    groups = defaultdict(
        list
    )

    for trade in trades:
        value = getattr(
            trade,
            field,
            None,
        )

        if value is None:
            value = "Unspecified"

        value = (
            str(value)
            .strip()
            or "Unspecified"
        )

        groups[value].append(
            trade
        )

    result = {}

    for name, items in groups.items():
        profits = [
            _profit(item)
            for item in items
        ]

        wins = len([
            value
            for value
            in profits
            if value > 0
        ])

        losses = len([
            value
            for value
            in profits
            if value < 0
        ])

        breakeven = len([
            value
            for value
            in profits
            if value == 0
        ])

        total = len(
            items
        )

        gross_profit = sum(
            value
            for value
            in profits
            if value > 0
        )

        gross_loss = abs(
            sum(
                value
                for value
                in profits
                if value < 0
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

        result[name] = {
            "trades":
                total,

            "wins":
                wins,

            "losses":
                losses,

            "breakeven":
                breakeven,

            "win_rate":
                round(
                    wins /
                    total *
                    100,
                    2,
                )
                if total
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
                    total,
                    2,
                )
                if total
                else 0.0,

            "profit_factor":
                round(
                    profit_factor,
                    2,
                ),
        }

    return result
