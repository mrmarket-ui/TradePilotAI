from collections import defaultdict

from sqlalchemy.orm import Session

from models.trade import Trade


def get_equity_curve(db: Session, user_id: int):

    trades = (
        db.query(Trade)
        .filter(
            Trade.user_id == user_id
        )
        .order_by(Trade.closed_at)
        .all()
    )

    balance = 0
    equity = []

    for trade in trades:

        if trade.closed_at is None:
            continue

        balance += trade.profit or 0

        equity.append(
            {
                "date": trade.closed_at.strftime("%Y-%m-%d"),
                "balance": round(balance, 2)
            }
        )

    return equity


def get_monthly_profit(db: Session, user_id: int):

    trades = (
        db.query(Trade)
        .filter(
            Trade.user_id == user_id
        )
        .all()
    )

    monthly = defaultdict(float)

    for trade in trades:

        if trade.closed_at is None:
            continue

        month = trade.closed_at.strftime("%Y-%m")

        monthly[month] += trade.profit or 0

    return [
        {
            "month": month,
            "profit": round(profit, 2)
        }
        for month, profit in sorted(monthly.items())
    ]


def get_win_loss(db: Session, user_id: int):

    trades = (
        db.query(Trade)
        .filter(
            Trade.user_id == user_id
        )
        .all()
    )

    wins = sum(
        1 for trade in trades
        if (trade.profit or 0) > 0
    )

    losses = sum(
        1 for trade in trades
        if (trade.profit or 0) < 0
    )

    breakeven = len(trades) - wins - losses

    return {
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven
    }


def get_pair_performance(db: Session, user_id: int):

    trades = (
        db.query(Trade)
        .filter(
            Trade.user_id == user_id
        )
        .all()
    )

    performance = defaultdict(float)

    for trade in trades:

        performance[trade.pair] += trade.profit or 0

    return [
        {
            "pair": pair,
            "profit": round(profit, 2)
        }
        for pair, profit in sorted(
            performance.items(),
            key=lambda x: x[1],
            reverse=True
        )
    ]