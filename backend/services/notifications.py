"""
In-app notifications.

Anything that happens to a person's account (a new sign-in, a password change,
a billing event, an announcement from the owner) can be recorded here and shows
up under the bell in the top bar.

notify_safely() is what other features should call: a problem in the
notification system must never break the thing that triggered it.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.notification import Notification
from models.user import User

logger = logging.getLogger("tradepilot.notifications")

SEVERITIES = ("info", "success", "warning", "security")
MAX_PER_USER = 200


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def safe_link(link: object) -> str | None:
    """Only links that stay inside the app are kept (no other websites)."""

    value = str(link or "").strip()

    if (
        not value
        or len(value) > 255
        or not value.startswith("/")
        or value.startswith("//")
        or "\\" in value
        or any(ord(ch) < 32 for ch in value)
    ):
        return None

    return value


def _clean_severity(severity: str) -> str:
    return severity if severity in SEVERITIES else "info"


def _prune(db: Session, user_id: int) -> None:
    total = (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == user_id)
        .scalar()
        or 0
    )

    if total <= MAX_PER_USER:
        return

    oldest = (
        db.query(Notification.id)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.id.asc())
        .limit(total - MAX_PER_USER)
        .all()
    )

    db.query(Notification).filter(
        Notification.id.in_([row.id for row in oldest])
    ).delete(synchronize_session=False)


def notify(
    db: Session,
    user_id: int,
    type: str,
    title: str,
    body: str | None = None,
    link: str | None = None,
    severity: str = "info",
    dedupe_within: timedelta | None = None,
) -> Notification | None:
    """
    Records a notification. With dedupe_within, an identical notification
    (same type and text) created inside that window is not repeated.
    """

    now = _now()

    if dedupe_within is not None:
        existing = (
            db.query(Notification.id)
            .filter(
                Notification.user_id == user_id,
                Notification.type == type,
                Notification.body == body,
                Notification.created_at >= now - dedupe_within,
            )
            .first()
        )

        if existing is not None:
            return None

    row = Notification(
        user_id=user_id,
        type=type[:60],
        severity=_clean_severity(severity),
        title=title[:160],
        body=body,
        link=safe_link(link),
        created_at=now,
    )

    db.add(row)
    db.flush()
    _prune(db, user_id)
    db.commit()
    db.refresh(row)

    return row


def notify_safely(db: Session, *args, **kwargs) -> Notification | None:
    try:
        return notify(db, *args, **kwargs)
    except Exception as exc:
        db.rollback()
        logger.error("Could not record a notification: %s", type(exc).__name__)
        return None


def unread_count(db: Session, user_id: int) -> int:
    return (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
        .scalar()
        or 0
    )


def list_notifications(
    db: Session,
    user_id: int,
    limit: int = 20,
    unread_only: bool = False,
    before_id: int | None = None,
) -> list[Notification]:
    query = db.query(Notification).filter(Notification.user_id == user_id)

    if unread_only:
        query = query.filter(Notification.read_at.is_(None))

    if before_id is not None:
        query = query.filter(Notification.id < before_id)

    return query.order_by(Notification.id.desc()).limit(limit).all()


def mark_read(db: Session, user_id: int, notification_id: int) -> bool:
    row = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first()
    )

    if row is None:
        return False

    if row.read_at is None:
        row.read_at = _now()
        db.commit()

    return True


def mark_all_read(db: Session, user_id: int) -> int:
    changed = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
        .update({Notification.read_at: _now()}, synchronize_session=False)
    )
    db.commit()

    return int(changed)


def broadcast(
    db: Session,
    title: str,
    body: str | None,
    link: str | None,
    severity: str = "info",
) -> int:
    """An announcement from the owner to every active account."""

    now = _now()
    ids = [row.id for row in db.query(User.id).filter(User.is_active.is_(True)).all()]

    db.bulk_insert_mappings(
        Notification,
        [
            {
                "user_id": user_id,
                "type": "announcement",
                "severity": _clean_severity(severity),
                "title": title[:160],
                "body": body,
                "link": safe_link(link),
                "created_at": now,
            }
            for user_id in ids
        ],
    )
    db.commit()

    return len(ids)
