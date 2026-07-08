from sqlalchemy.orm import Session
from sqlalchemy import func

from models.trade import Trade


def calculate_statistics(
    db: Session,
    user_id: int
):
    trades = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .all()
    )

    if not trades:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "net_profit": 0,
            "gross_profit": 0,
            "gross_loss": 0,
            "average_win": 0,
            "average_loss": 0,
            "profit_factor": 0,
            "best_trade": 0,
            "worst_trade": 0,
        }

    total_trades = len(trades)

    wins = [t for t in trades if (t.profit or 0) > 0]
    losses = [t for t in trades if (t.profit or 0) < 0]

    gross_profit = sum(t.profit or 0 for t in wins)
    gross_loss = abs(sum(t.profit or 0 for t in losses))

    net_profit = gross_profit - gross_loss

    average_win = (
        gross_profit / len(wins)
        if wins else 0
    )

    average_loss = (
        gross_loss / len(losses)
        if losses else 0
    )

    win_rate = (
        len(wins) / total_trades * 100
        if total_trades else 0
    )

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0 else gross_profit
    )

    best_trade = max(
        (t.profit or 0 for t in trades),
        default=0
    )

    worst_trade = min(
        (t.profit or 0 for t in trades),
        default=0
    )

    return {
        "total_trades": total_trades,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": round(win_rate, 2),
        "net_profit": round(net_profit, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "average_win": round(average_win, 2),
        "average_loss": round(average_loss, 2),
        "profit_factor": round(profit_factor, 2),
        "best_trade": round(best_trade, 2),
        "worst_trade": round(worst_trade, 2),
    }