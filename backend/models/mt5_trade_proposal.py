from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)

from database.database import Base


class MT5TradeProposal(Base):
    __tablename__ = "mt5_trade_proposals"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    broker_account_id = Column(
        Integer,
        ForeignKey(
            "broker_accounts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    strategy_profile_id = Column(
        Integer,
        ForeignKey(
            "strategy_profiles.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    symbol = Column(
        String,
        nullable=False,
        index=True,
    )

    direction = Column(
        String,
        nullable=False,
    )

    entry_price = Column(
        Float,
        nullable=False,
    )

    stop_loss = Column(
        Float,
        nullable=False,
    )

    take_profit = Column(
        Float,
        nullable=False,
    )

    risk_percent = Column(
        Float,
        nullable=False,
    )

    risk_reward = Column(
        Float,
        nullable=False,
    )

    max_hold_minutes = Column(
        Integer,
        nullable=False,
        default=30,
    )

    timeframe_context = Column(
        JSON,
        nullable=True,
    )

    matched_rules = Column(
        JSON,
        nullable=True,
    )

    missing_rules = Column(
        JSON,
        nullable=True,
    )

    strategy_snapshot = Column(
        JSON,
        nullable=True,
    )

    analysis_summary = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String,
        nullable=False,
        default="pending",
        index=True,
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )

    approved_at = Column(
        DateTime,
        nullable=True,
    )

    rejected_at = Column(
        DateTime,
        nullable=True,
    )

    executed_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
