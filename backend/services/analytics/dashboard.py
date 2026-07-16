from sqlalchemy.orm import Session
from sqlalchemy import func

from models.trade import Trade


def dashboard_summary(db: Session, user_id: int):

    trades = db.query(Trade).filter(
        Trade.user_id == user_id
    ).all()

    total_trades = len(trades)

    if total_trades == 0:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "net_profit": 0,
            "gross_profit": 0,
            "gross_loss": 0,
            "average_profit": 0,
            "best_trade": 0,
            "worst_trade": 0,
            "profit_factor": 0
        }

    wins = [t for t in trades if t.profit > 0]
    losses = [t for t in trades if t.profit <= 0]

    gross_profit = sum(t.profit for t in wins)
    gross_loss = abs(sum(t.profit for t in losses))

    net_profit = gross_profit - gross_loss

    average_profit = sum(
        t.profit for t in trades
    ) / total_trades

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0 else gross_profit
    )

    return {

        "total_trades": total_trades,

        "wins": len(wins),

        "losses": len(losses),

        "win_rate": round(
            len(wins) / total_trades * 100,
            2
        ),

        "net_profit": round(net_profit, 2),

        "gross_profit": round(gross_profit, 2),

        "gross_loss": round(gross_loss, 2),

        "average_profit": round(
            average_profit,
            2
        ),

        "best_trade": round(
            max(t.profit for t in trades),
            2
        ),

        "worst_trade": round(
            min(t.profit for t in trades),
            2
        ),

        "profit_factor": round(
            profit_factor,
            2
        )
    }