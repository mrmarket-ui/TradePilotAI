from sqlalchemy.orm import Session
from sqlalchemy import func

from models.trade import Trade


class AnalyticsEngine:

    @staticmethod
    def total_profit(db: Session, user_id: int):

        value = db.query(
            func.sum(Trade.profit)
        ).filter(
            Trade.user_id == user_id
        ).scalar()

        return round(value or 0, 2)

    @staticmethod
    def total_trades(db: Session, user_id: int):

        return db.query(Trade).filter(
            Trade.user_id == user_id
        ).count()

    @staticmethod
    def winning_trades(db: Session, user_id: int):

        return db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.profit > 0
        ).count()

    @staticmethod
    def losing_trades(db: Session, user_id: int):

        return db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.profit < 0
        ).count()

    @staticmethod
    def breakeven_trades(db: Session, user_id: int):

        return db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.profit == 0
        ).count()

    @staticmethod
    def win_rate(db: Session, user_id: int):

        total = AnalyticsEngine.total_trades(
            db,
            user_id
        )

        if total == 0:
            return 0

        wins = AnalyticsEngine.winning_trades(
            db,
            user_id
        )

        return round((wins / total) * 100, 2)

    @staticmethod
    def average_win(db: Session, user_id: int):

        value = db.query(
            func.avg(Trade.profit)
        ).filter(
            Trade.user_id == user_id,
            Trade.profit > 0
        ).scalar()

        return round(value or 0, 2)

    @staticmethod
    def average_loss(db: Session, user_id: int):

        value = db.query(
            func.avg(Trade.profit)
        ).filter(
            Trade.user_id == user_id,
            Trade.profit < 0
        ).scalar()

        return round(value or 0, 2)

    @staticmethod
    def profit_factor(db: Session, user_id: int):

        gross_profit = db.query(
            func.sum(Trade.profit)
        ).filter(
            Trade.user_id == user_id,
            Trade.profit > 0
        ).scalar() or 0

        gross_loss = db.query(
            func.sum(Trade.profit)
        ).filter(
            Trade.user_id == user_id,
            Trade.profit < 0
        ).scalar() or 0

        gross_loss = abs(gross_loss)

        if gross_loss == 0:
            return gross_profit

        return round(gross_profit / gross_loss, 2)

    @staticmethod
    def average_rr(db: Session, user_id: int):

        trades = db.query(Trade).filter(
            Trade.user_id == user_id
        ).all()

        values = []

        for trade in trades:

            risk = abs(trade.entry - trade.stop_loss)

            reward = abs(trade.exit_price - trade.entry)

            if risk == 0:
                continue

            values.append(reward / risk)

        if not values:
            return 0

        return round(sum(values) / len(values), 2)

    @staticmethod
    def dashboard(db: Session, user_id: int):

        return {

            "total_profit":
                AnalyticsEngine.total_profit(
                    db,
                    user_id
                ),

            "total_trades":
                AnalyticsEngine.total_trades(
                    db,
                    user_id
                ),

            "wins":
                AnalyticsEngine.winning_trades(
                    db,
                    user_id
                ),

            "losses":
                AnalyticsEngine.losing_trades(
                    db,
                    user_id
                ),

            "breakeven":
                AnalyticsEngine.breakeven_trades(
                    db,
                    user_id
                ),

            "win_rate":
                AnalyticsEngine.win_rate(
                    db,
                    user_id
                ),

            "average_win":
                AnalyticsEngine.average_win(
                    db,
                    user_id
                ),

            "average_loss":
                AnalyticsEngine.average_loss(
                    db,
                    user_id
                ),

            "profit_factor":
                AnalyticsEngine.profit_factor(
                    db,
                    user_id
                ),

            "average_rr":
                AnalyticsEngine.average_rr(
                    db,
                    user_id
                )
        }
