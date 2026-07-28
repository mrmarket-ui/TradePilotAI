from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from database.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

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
        unique=True,
        index=True,
    )

    provider = Column(
        String(30),
        nullable=False,
        default="paypal",
    )

    plan = Column(
        String(30),
        nullable=False,
        default="free",
        index=True,
    )

    status = Column(
        String(40),
        nullable=False,
        default="inactive",
        index=True,
    )

    paypal_subscription_id = Column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
    )

    paypal_plan_id = Column(
        String(100),
        nullable=True,
    )

    paypal_payer_id = Column(
        String(100),
        nullable=True,
    )

    payer_email = Column(
        String(255),
        nullable=True,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="USD",
    )

    amount = Column(
        String(30),
        nullable=True,
    )

    current_period_start = Column(
        DateTime,
        nullable=True,
    )

    current_period_end = Column(
        DateTime,
        nullable=True,
    )

    next_billing_at = Column(
        DateTime,
        nullable=True,
    )

    cancelled_at = Column(
        DateTime,
        nullable=True,
    )

    last_payment_at = Column(
        DateTime,
        nullable=True,
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

    user = relationship(
        "User",
        back_populates="subscription",
    )
