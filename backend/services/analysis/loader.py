"""
TradePilot AI analysis trade loader.

Excludes deposits, withdrawals, bonuses, balance adjustments,
credits, and other non-market account operations.
"""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.trade import Trade


EXCLUDED_PAIRS = {
    "balance",
    "bonus",
    "credit",
    "deposit",
    "withdrawal",
    "withdraw",
    "adjustment",
    "commission",
    "swap",
    "transfer",
    "cash",
}


def load_user_trades(
    db: Session,
    user_id: int,
) -> list[Trade]:
    """
    Load genuine market trades belonging to the user.
    """

    normalized_pair = func.lower(
        func.trim(
            func.coalesce(Trade.pair, "")
        )
    )

    return (
        db.query(Trade)
        .filter(
            Trade.user_id == user_id,
            ~normalized_pair.in_(EXCLUDED_PAIRS),
        )
        .order_by(
            Trade.closed_at.asc(),
            Trade.created_at.asc(),
        )
        .all()
    )
