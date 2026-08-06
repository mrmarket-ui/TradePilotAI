from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)

from database.database import Base


class StrategySource(Base):
    __tablename__ = "strategy_sources"

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

    source_type = Column(
        String(30),
        nullable=False,
        index=True,
    )

    original_name = Column(
        String(255),
        nullable=True,
    )

    source_url = Column(
        Text,
        nullable=True,
    )

    mime_type = Column(
        String(120),
        nullable=True,
    )

    file_path = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="uploaded",
        index=True,
    )

    extracted_text = Column(
        Text,
        nullable=True,
    )

    extracted_strategy = Column(
        JSON,
        nullable=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    analyzed_at = Column(
        DateTime,
        nullable=True,
    )
