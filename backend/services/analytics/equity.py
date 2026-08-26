from __future__ import annotations

from datetime import datetime
from typing import Iterable


def _trade_time(trade):
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


def build_equity_curve(
    trades: Iterable,
    starting_balance: float = 0.0,
) -> list[dict]:
    ordered = sorted(
        list(trades),
        key=lambda trade:
            _trade_time(
                trade
            )
            or datetime.min,
    )

    balance = float(
        starting_balance
    )

    peak = balance

    curve = []

    for trade in ordered:
        profit = float(
            getattr(
                trade,
                "profit",
                None,
            )
            or 0
        )

        balance += profit

        if balance > peak:
            peak = balance

        drawdown = (
            peak -
            balance
        )

        drawdown_percent = (
            drawdown /
            peak *
            100
            if peak > 0
            else 0.0
        )

        timestamp = (
            _trade_time(
                trade
            )
        )

        curve.append({
            "trade_id":
                getattr(
                    trade,
                    "id",
                    None,
                ),

            "date":
                timestamp.isoformat()
                if timestamp
                else None,

            "balance":
                round(
                    balance,
                    2,
                ),

            "profit":
                round(
                    profit,
                    2,
                ),

            "peak":
                round(
                    peak,
                    2,
                ),

            "drawdown":
                round(
                    drawdown,
                    2,
                ),

            "drawdown_percent":
                round(
                    drawdown_percent,
                    2,
                ),
        })

    return curve


def calculate_drawdown(
    trades: Iterable,
    starting_balance: float = 0.0,
) -> dict:
    curve = (
        build_equity_curve(
            trades,
            starting_balance=
                starting_balance,
        )
    )

    if not curve:
        return {
            "max_drawdown": 0.0,
            "max_drawdown_percent": 0.0,
        }

    max_drawdown = max(
        point["drawdown"]
        for point in curve
    )

    max_drawdown_percent = max(
        point[
            "drawdown_percent"
        ]
        for point in curve
    )

    return {
        "max_drawdown":
            round(
                max_drawdown,
                2,
            ),

        "max_drawdown_percent":
            round(
                max_drawdown_percent,
                2,
            ),
    }
