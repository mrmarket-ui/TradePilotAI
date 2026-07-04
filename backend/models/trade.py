from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
)

from sqlalchemy.orm import relationship

from database.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)

    # Relationship
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # Broker Information
    broker = Column(String, nullable=True)
    ticket = Column(String, unique=True, index=True, nullable=True)

    # Trade Information
    pair = Column(String, nullable=False)
    direction = Column(String, nullable=False)

    entry = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)

    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)

    lot_size = Column(Float, nullable=True)

    # Results
    profit = Column(Float, nullable=True)
    commission = Column(Float, default=0)
    swap = Column(Float, default=0)

    # MT5 Metadata
    magic_number = Column(Integer, nullable=True)
    comment = Column(String, nullable=True)

    # Trading Journal
    strategy = Column(String, nullable=True)
    emotion = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    # Times
    opened_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Import Status
    imported = Column(
        Boolean,
        default=False
    )

    # Relationship
    user = relationship(
        "User",
        back_populates="trades"
    )