from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash = Column(
        String,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    # Profile
    full_name = Column(
        String,
        nullable=True,
    )

    username = Column(
        String,
        unique=True,
        nullable=True,
    )

    avatar = Column(
        String,
        nullable=True,
    )

    bio = Column(
        String,
        nullable=True,
    )

    # Subscription access level
    plan = Column(
        String,
        default="free",
        nullable=False,
    )

    # International preferences
    preferred_language = Column(
        String(10),
        default="en",
        nullable=False,
    )

    preferred_currency = Column(
        String(10),
        default="USD",
        nullable=False,
    )
    # Permissions
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_admin = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # AI Credits
    ai_credits = Column(
        Integer,
        default=20,
        nullable=False,
    )

    # Relationships
    trades = relationship(
        "Trade",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    broker_accounts = relationship(
        "BrokerAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    subscription = relationship(
        "Subscription",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
