from datetime import datetime

from sqlalchemy import (
    Boolean,
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


class AISignal(Base):
    __tablename__ = "ai_signals"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    strategy_id = Column(
        Integer,
        ForeignKey(
            "strategy_profiles.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    symbol = Column(
        String(30),
        nullable=False,
    )

    timeframe = Column(
        String(20),
        nullable=True,
    )

    direction = Column(
        String(20),
        nullable=False,
    )

    confidence = Column(
        Float,
        nullable=False,
        default=0,
    )

    setup_score = Column(
        Float,
        nullable=False,
        default=0,
    )

    entry_low = Column(
        Float,
        nullable=True,
    )

    entry_high = Column(
        Float,
        nullable=True,
    )

    stop_loss = Column(
        Float,
        nullable=True,
    )

    take_profit_1 = Column(
        Float,
        nullable=True,
    )

    take_profit_2 = Column(
        Float,
        nullable=True,
    )

    take_profit_3 = Column(
        Float,
        nullable=True,
    )

    risk_reward = Column(
        Float,
        nullable=True,
    )

    matched_rules = Column(
        JSON,
        nullable=False,
        default=list,
    )

    missing_rules = Column(
        JSON,
        nullable=False,
        default=list,
    )

    reasoning = Column(
        Text,
        nullable=True,
    )

    invalidation = Column(
        Text,
        nullable=True,
    )

    chart_path = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="generated",
    )

    user_approved = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )


class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    signal_id = Column(
        Integer,
        ForeignKey(
            "ai_signals.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    symbol = Column(
        String(30),
        nullable=False,
    )

    direction = Column(
        String(20),
        nullable=False,
    )

    entry_price = Column(
        Float,
        nullable=False,
    )

    stop_loss = Column(
        Float,
        nullable=True,
    )

    take_profit = Column(
        Float,
        nullable=True,
    )

    risk_percent = Column(
        Float,
        nullable=False,
        default=0.5,
    )

    status = Column(
        String(20),
        nullable=False,
        default="open",
    )

    exit_price = Column(
        Float,
        nullable=True,
    )

    profit_loss = Column(
        Float,
        nullable=True,
    )

    opened_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    closed_at = Column(
        DateTime,
        nullable=True,
    )
