from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.trade import Trade


def save_trade(
    db: Session,
    trade: Trade,
):
    existing = (
        db.query(Trade)
        .filter(
            Trade.ticket == trade.ticket,
            Trade.user_id == trade.user_id,
        )
        .first()
    )

    if existing:
        return False

    try:
        db.add(trade)
        db.commit()

        return True

    except IntegrityError:
        db.rollback()

        # The current database has a global UNIQUE
        # constraint on Trade.ticket. Treat an
        # already-existing MT5 ticket as skipped
        # instead of crashing the whole sync.
        duplicate = (
            db.query(Trade)
            .filter(
                Trade.ticket == trade.ticket
            )
            .first()
        )

        if duplicate:
            return False

        raise
