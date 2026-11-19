from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.admin import require_admin
from models.notification import Notification
from models.user import User
from services import notifications as service
from services.dependencies import get_current_user

router = APIRouter()


def _out(row: Notification) -> dict:
    return {
        "id": row.id,
        "type": row.type,
        "severity": row.severity,
        "title": row.title,
        "body": row.body,
        "link": row.link,
        "read": row.read_at is not None,
        "created_at": row.created_at,
    }


@router.get("/notifications")
def list_my_notifications(
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    before_id: int | None = Query(None, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = service.list_notifications(
        db, current_user.id, limit=limit, unread_only=unread_only, before_id=before_id
    )

    return {
        "items": [_out(row) for row in rows],
        "unread": service.unread_count(db, current_user.id),
        "next_before_id": rows[-1].id if len(rows) == limit else None,
    }


@router.get("/notifications/unread-count")
def my_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"unread": service.unread_count(db, current_user.id)}


@router.post("/notifications/read-all")
def read_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"marked": service.mark_all_read(db, current_user.id)}


@router.post("/notifications/{notification_id}/read")
def read_one(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not service.mark_read(db, current_user.id, notification_id):
        raise HTTPException(status_code=404, detail="Notification not found.")

    return {"ok": True}


class BroadcastBody(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    body: str | None = Field(default=None, max_length=2000)
    link: str | None = Field(default=None, max_length=255)
    severity: Literal["info", "success", "warning"] = "info"


@router.post("/admin/notifications/broadcast", status_code=201)
def broadcast_announcement(
    payload: BroadcastBody,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if payload.link and service.safe_link(payload.link) is None:
        raise HTTPException(
            status_code=422,
            detail="The link must be a page inside the app, such as /billing.",
        )

    sent = service.broadcast(
        db,
        title=payload.title.strip(),
        body=payload.body.strip() if payload.body else None,
        link=payload.link,
        severity=payload.severity,
    )

    return {"sent_to": sent}
