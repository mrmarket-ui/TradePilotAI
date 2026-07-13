from __future__ import annotations

from typing import Any


def calculate_weekly_metrics(
    trades: list[Any],
) -> dict:
    profits = [
        float(getattr(trade, "profit", 0) or 0)
        for trade in trades
    ]

    winners = [
        profit
        for profit in profits
        if profit > 0
    ]

    losers = [
        profit
        for profit in profits
        if profit < 0
    ]

    breakeven = [
        profit
        for profit in profits
        if profit == 0
    ]

    gross_profit = sum(winners)
    gross_loss = abs(sum(losers))
    net_profit = sum(profits)

    total = len(profits)

    win_rate = (
        len(winners) / total * 100
        if total else 0
    )

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else gross_profit
    )

    return {
        "total_trades": total,
        "wins": len(winners),
        "losses": len(losers),
        "breakeven": len(breakeven),
        "win_rate": round(win_rate, 2),
        "net_profit": round(net_profit, 2),
        "profit_factor": round(profit_factor, 2),
        "best_trade": round(
            max(profits, default=0),
            2,
        ),
        "worst_trade": round(
            min(profits, default=0),
            2,
        ),
    }
