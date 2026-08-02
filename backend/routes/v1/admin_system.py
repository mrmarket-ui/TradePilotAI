from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.admin import require_admin

from models.paypal_webhook_event import (
    PayPalWebhookEvent,
)
from models.user import User


router = APIRouter(
    prefix="/admin/system",
    tags=["Admin System"],
)


@router.get("/health")
def admin_system_health(
    db: Session = Depends(get_db),
    admin_user: User = Depends(
        require_admin,
    ),
):
    database_status = "healthy"

    try:
        db.execute(
            text("SELECT 1")
        )
    except Exception:
        database_status = "unhealthy"

    return {
        "api": "healthy",
        "database": database_status,
    }


@router.get("/webhooks")
def admin_webhook_events(
    processing_status: str | None = Query(
        default=None,
        max_length=30,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
    admin_user: User = Depends(
        require_admin,
    ),
):
    query = db.query(
        PayPalWebhookEvent
    )

    if processing_status:
        query = query.filter(
            PayPalWebhookEvent.processing_status
            == processing_status.strip().lower()
        )

    total = query.count()

    events = (
        query
        .order_by(
            PayPalWebhookEvent.received_at.desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "events": [
            {
                "id": event.id,
                "paypal_event_id":
                    event.paypal_event_id,
                "event_type":
                    event.event_type,
                "resource_id":
                    event.resource_id,
                "processing_status":
                    event.processing_status,
                "error_message":
                    event.error_message,
                "received_at":
                    event.received_at,
                "processed_at":
                    event.processed_at,
            }
            for event in events
        ],
    }
