from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime
)

from sqlalchemy.orm import relationship
from datetime import datetime

from database.database import Base


class BrokerAccount(Base):
    __tablename__ = "broker_accounts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    strategy_profile_id = Column(
        Integer,
        ForeignKey("strategy_profiles.id"),
        nullable=True,
        index=True,
    )

    broker = Column(String, nullable=False)

    server = Column(String, nullable=False)

    account_number = Column(String, nullable=False)

    encrypted_password = Column(String, nullable=False)

    connected = Column(Boolean, default=False)

    # AutoTrader monitoring settings.
    # Enabling this does NOT authorize live order execution.
    autotrader_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    max_hold_minutes = Column(
        Integer,
        nullable=False,
        default=30,
    )

    last_sync = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="broker_accounts"
    )

    strategy_profile = relationship(
        "StrategyProfile"
    )

