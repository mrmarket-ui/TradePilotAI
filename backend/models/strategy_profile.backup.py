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


class StrategyProfile(Base):
    __tablename__ = "strategy_profiles"

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

    name = Column(
        String(120),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    markets = Column(
        JSON,
        nullable=False,
        default=list,
    )

    sessions = Column(
        JSON,
        nullable=False,
        default=list,
    )

    timeframes = Column(
        JSON,
        nullable=False,
        default=list,
    )

    entry_rules = Column(
        JSON,
        nullable=False,
        default=list,
    )

    exit_rules = Column(
        JSON,
        nullable=False,
        default=list,
    )

    confirmations = Column(
        JSON,
        nullable=False,
        default=list,
    )

    psychology_rules = Column(
        JSON,
        nullable=False,
        default=list,
    )

    trade_management_rules = Column(
        JSON,
        nullable=False,
        default=list,
    )

    max_risk_percent = Column(
        Float,
        nullable=False,
        default=0.5,
    )

    max_daily_loss_percent = Column(
        Float,
        nullable=False,
        default=2.0,
    )

    max_weekly_loss_percent = Column(
        Float,
        nullable=False,
        default=5.0,
    )

    max_trades_per_day = Column(
        Integer,
        nullable=False,
        default=3,
    )

    max_consecutive_losses = Column(
        Integer,
        nullable=False,
        default=2,
    )

    requires_user_approval = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
