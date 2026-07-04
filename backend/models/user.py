from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)

    password_hash = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Profile
    full_name = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=True)
    avatar = Column(String, nullable=True)
    bio = Column(String, nullable=True)

    # Subscription
    plan = Column(String, default="free")

    # Permissions
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # AI Credits
    ai_credits = Column(Integer, default=20)

    # Relationships
    trades = relationship(
        "Trade",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    broker_accounts = relationship(
        "BrokerAccount",
        back_populates="user",
        cascade="all, delete-orphan"
    )