from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

from models.trade import Trade
from services.analysis.loader import load_user_trades


def calculate_statistics_from_trades(
    trades: Iterable[Trade],
) -> dict:
    trades = list(trades)

    if not trades:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "breakeven": 0,
            "win_rate": 0.0,
            "net_profit": 0.0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "average_win": 0.0,
            "average_loss": 0.0,
            "profit_factor": 0.0,
            "best_trade": 0.0,
            "worst_trade": 0.0,
        }

    wins = [
        trade
        for trade in trades
        if float(trade.profit or 0) > 0
    ]

    losses = [
        trade
        for trade in trades
        if float(trade.profit or 0) < 0
    ]

    breakeven = [
        trade
        for trade in trades
        if float(trade.profit or 0) == 0
    ]

    gross_profit = sum(
        float(trade.profit or 0)
        for trade in wins
    )

    gross_loss = abs(
        sum(
            float(trade.profit or 0)
            for trade in losses
        )
    )

    total_trades = len(trades)
    net_profit = gross_profit - gross_loss

    average_win = (
        gross_profit / len(wins)
        if wins else 0.0
    )

    average_loss = (
        gross_loss / len(losses)
        if losses else 0.0
    )

    win_rate = (
        len(wins) / total_trades * 100
        if total_trades else 0.0
    )

    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = gross_profit
    else:
        profit_factor = 0.0

    profits = [
        float(trade.profit or 0)
        for trade in trades
    ]

    return {
        "total_trades": total_trades,
        "wins": len(wins),
        "losses": len(losses),
        "breakeven": len(breakeven),
        "win_rate": round(win_rate, 2),
        "net_profit": round(net_profit, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "average_win": round(average_win, 2),
        "average_loss": round(average_loss, 2),
        "profit_factor": round(profit_factor, 2),
        "best_trade": round(max(profits), 2),
        "worst_trade": round(min(profits), 2),
    }


def calculate_statistics(
    db: Session,
    user_id: int,
) -> dict:
    trades = load_user_trades(
        db=db,
        user_id=user_id,
    )

    return calculate_statistics_from_trades(trades)
