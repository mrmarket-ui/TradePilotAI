"""
In-app notifications (the bell in the top bar).

One row per notification per user. Rows are only ever read through queries
that filter on the signed-in user's id.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text

from database.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type = Column(String(60), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default="info")
    title = Column(String(160), nullable=False)
    body = Column(Text, nullable=True)
    link = Column(String(255), nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now)

    __table_args__ = (
        Index("ix_notifications_user_unread", "user_id", "read_at"),
    )
