"""
TradePilot AI unified dashboard service.

Combines:
- Trading statistics
- Equity curve
- Monthly performance
- Symbol activity
- Recent trades
- AI dashboard intelligence
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy.orm import Session

from services.analysis.loader import load_user_trades
from services.analysis.service import AnalysisService
from services.analytics.engine import calculate_statistics_from_trades
from services.dashboard.intelligence.engine import (
    generate_dashboard_intelligence,
)


def _serialize_trade(trade: Any) -> dict:
    """Convert a Trade model into dashboard-safe data."""

    return {
        "id": trade.id,
        "pair": trade.pair,
        "direction": trade.direction,
        "profit": round(float(trade.profit or 0), 2),
        "lot_size": trade.lot_size,
        "strategy": trade.strategy,
        "opened_at": trade.opened_at,
        "closed_at": trade.closed_at,
    }


def _build_equity_curve(trades: list) -> list[dict]:
    """Build cumulative realized-profit equity data."""

    closed_trades = sorted(
        [
            trade
            for trade in trades
            if trade.closed_at is not None
        ],
        key=lambda trade: trade.closed_at,
    )

    equity_curve = []
    balance = 0.0

    for trade in closed_trades:
        balance += float(trade.profit or 0)

        equity_curve.append({
            "date": trade.closed_at,
            "balance": round(balance, 2),
        })

    return equity_curve


def _build_monthly_profit(trades: list) -> dict:
    """Aggregate realized profit by calendar month."""

    monthly_profit: dict[str, float] = {}

    for trade in trades:
        if trade.closed_at is None:
            continue

        month = trade.closed_at.strftime("%Y-%m")

        monthly_profit[month] = (
            monthly_profit.get(month, 0.0)
            + float(trade.profit or 0)
        )

    return {
        month: round(profit, 2)
        for month, profit in sorted(
            monthly_profit.items()
        )
    }


def _build_symbol_activity(trades: list) -> list[dict]:
    """Count genuine trades per market symbol."""

    counter = Counter(
        trade.pair
        for trade in trades
        if trade.pair
    )

    return [
        {
            "pair": pair,
            "count": count,
        }
        for pair, count in counter.most_common()
    ]


def get_dashboard(
    db: Session,
    user_id: int,
) -> dict:
    """
    Return the complete TradePilot AI dashboard payload.
    """

    trades = load_user_trades(
        db=db,
        user_id=user_id,
    )

    statistics = calculate_statistics_from_trades(
        trades
    )

    analysis = AnalysisService.analyze(
        db=db,
        user_id=user_id,
    )

    intelligence = generate_dashboard_intelligence(
        analysis
    )

    recent_trades = sorted(
        trades,
        key=lambda trade: (
            trade.closed_at
            or trade.opened_at
            or trade.created_at
        ),
        reverse=True,
    )[:10]

    return {
        "intelligence": intelligence,
        "summary": statistics,
        "equity_curve": _build_equity_curve(
            trades
        ),
        "monthly_profit": _build_monthly_profit(
            trades
        ),
        "symbols": _build_symbol_activity(
            trades
        ),
        "recent_trades": [
            _serialize_trade(trade)
            for trade in recent_trades
        ],
        "trader_dna": analysis.trader_dna,
        "recommendations": analysis.recommendations[:5],
    }
