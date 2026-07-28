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

    # Identity
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

    # General information
    name = Column(
        String(120),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    strategy_type = Column(
        String(40),
        nullable=False,
        default="Day Trading",
    )

    version = Column(
        String(20),
        nullable=False,
        default="1.0",
    )

    icon = Column(
        String(50),
        nullable=True,
    )

    color = Column(
        String(20),
        nullable=True,
        default="#2563EB",
    )

    is_favorite = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    ai_notes = Column(
        Text,
        nullable=True,
    )

    # Markets and direction
    markets = Column(
        JSON,
        nullable=False,
        default=list,
    )

    allowed_symbols = Column(
        JSON,
        nullable=False,
        default=list,
    )

    blocked_symbols = Column(
        JSON,
        nullable=False,
        default=list,
    )

    preferred_direction = Column(
        String(10),
        nullable=False,
        default="BOTH",
    )

    # Trading schedule
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

    allowed_weekdays = Column(
        JSON,
        nullable=False,
        default=list,
    )

    trading_start_time = Column(
        String(10),
        nullable=True,
    )

    trading_end_time = Column(
        String(10),
        nullable=True,
    )

    timezone = Column(
        String(60),
        nullable=True,
        default="UTC",
    )

    # Strategy rules
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

    pre_trade_checklist = Column(
        JSON,
        nullable=False,
        default=list,
    )

    post_trade_checklist = Column(
        JSON,
        nullable=False,
        default=list,
    )

    # Risk management
    max_risk_percent = Column(
        Float,
        nullable=False,
        default=0.5,
    )

    min_risk_reward = Column(
        Float,
        nullable=False,
        default=2.0,
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

    max_open_positions = Column(
        Integer,
        nullable=False,
        default=1,
    )

    max_lot_size = Column(
        Float,
        nullable=True,
    )

    move_to_breakeven_at_rr = Column(
        Float,
        nullable=True,
        default=1.0,
    )

    partial_take_profit_percent = Column(
        Float,
        nullable=True,
        default=50.0,
    )

    # News protection
    avoid_high_impact_news = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    news_minutes_before = Column(
        Integer,
        nullable=False,
        default=30,
    )

    news_minutes_after = Column(
        Integer,
        nullable=False,
        default=30,
    )

    # AI and automation
    ai_setup_scoring_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    ai_coach_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    auto_chart_analysis = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    auto_journal_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    weekly_ai_review_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    monthly_ai_review_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    requires_user_approval = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    automation_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Status
    is_active = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    is_archived = Column(
        Boolean,
        nullable=False,
        default=False,
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
