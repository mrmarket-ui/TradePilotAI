from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database.database import Base


class BrokerAccount(Base):
    __tablename__ = "broker_accounts"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    broker = Column(String, nullable=False)

    server = Column(String, nullable=False)

    account_number = Column(String, nullable=False)

    encrypted_password = Column(String, nullable=False)

    connected = Column(Boolean, default=False)

    last_sync = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship(
        "User",
        back_populates="broker_accounts"
    )