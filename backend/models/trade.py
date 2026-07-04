from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime
)

from sqlalchemy.orm import relationship
from datetime import datetime

from database.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    user = relationship(
    "User",
    back_populates="trades"
)

    pair = Column(String, nullable=False)

    direction = Column(String, nullable=False)

    entry = Column(Float, nullable=False)

    stop_loss = Column(Float, nullable=False)

    take_profit = Column(Float, nullable=False)

    exit_price = Column(Float, nullable=True)

    lot_size = Column(Float, nullable=True)

    strategy = Column(String, nullable=True)

    emotion = Column(String, nullable=True)

    notes = Column(String, nullable=True)

    profit = Column(Float, nullable=True)