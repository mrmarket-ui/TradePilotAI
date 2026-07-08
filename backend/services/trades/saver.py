from sqlalchemy.orm import Session

from models.trade import Trade


def save_trade(
    db: Session,
    trade: Trade
):

    existing = db.query(Trade).filter(
        Trade.ticket == trade.ticket,
        Trade.user_id == trade.user_id
    ).first()

    if existing:
        return False

    db.add(trade)

    db.commit()

    return True