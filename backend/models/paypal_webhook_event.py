from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    JSON,
    String,
)

from database.database import Base


class PayPalWebhookEvent(Base):
    __tablename__ = "paypal_webhook_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    paypal_event_id = Column(
        String(120),
        nullable=False,
        unique=True,
        index=True,
    )

    event_type = Column(
        String(120),
        nullable=False,
        index=True,
    )

    resource_id = Column(
        String(120),
        nullable=True,
        index=True,
    )

    processing_status = Column(
        String(30),
        nullable=False,
        default="received",
        index=True,
    )

    payload = Column(
        JSON,
        nullable=False,
    )

    error_message = Column(
        String,
        nullable=True,
    )

    received_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    processed_at = Column(
        DateTime,
        nullable=True,
    )
