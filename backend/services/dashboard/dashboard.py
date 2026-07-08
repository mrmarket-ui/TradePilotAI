from sqlalchemy.orm import Session
from sqlalchemy import func

from models.trade import Trade
from services.analytics.engine import calculate_statistics


def get_dashboard(db: Session, user_id: int):

    stats = calculate_statistics(
        db=db,
        user_id=user_id
    )

    trades = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .all()
    )

    recent_trades = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .order_by(Trade.closed_at.desc())
        .limit(10)
        .all()
    )

    symbols = (
        db.query(
            Trade.pair,
            func.count(Trade.id)
        )
        .filter(Trade.user_id == user_id)
        .group_by(Trade.pair)
        .all()
    )

    monthly = {}

    for trade in trades:

        if trade.closed_at is None:
            continue

        month = trade.closed_at.strftime("%Y-%m")

        monthly.setdefault(month, 0)

        monthly[month] += trade.profit or 0

    equity = []

    balance = 0

    closed = sorted(
        [t for t in trades if t.closed_at],
        key=lambda t: t.closed_at
    )

    for trade in closed:

        balance += trade.profit or 0

        equity.append(
            {
                "date": trade.closed_at,
                "balance": round(balance, 2)
            }
        )

    return {

        "summary": stats,

        "equity_curve": equity,

        "monthly_profit": monthly,

        "symbols": [
            {
                "pair": pair,
                "count": count
            }
            for pair, count in symbols
        ],

        "recent_trades": [
            {
                "id": trade.id,
                "pair": trade.pair,
                "direction": trade.direction,
                "profit": trade.profit,
                "lot_size": trade.lot_size,
                "opened_at": trade.opened_at,
                "closed_at": trade.closed_at
            }
            for trade in recent_trades
        ]
    }