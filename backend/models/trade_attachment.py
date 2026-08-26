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


class TradeAttachment(Base):
    __tablename__ = "trade_attachments"

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
        index=True,
    )

    trade_id = Column(
        Integer,
        ForeignKey(
            "trades.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    attachment_type = Column(
        String(30),
        nullable=False,
        default="image",
    )

    stage = Column(
        String(30),
        nullable=False,
        default="general",
    )

    original_name = Column(
        String(255),
        nullable=False,
    )

    stored_name = Column(
        String(255),
        nullable=False,
        unique=True,
    )

    mime_type = Column(
        String(120),
        nullable=True,
    )

    file_path = Column(
        String(500),
        nullable=False,
    )

    file_size = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    trade = relationship(
        "Trade",
        back_populates="attachments",
    )
