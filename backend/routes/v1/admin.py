from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.admin import require_admin

from models.subscription import Subscription
from models.trade import Trade
from models.user import User


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get("/overview")
def admin_overview(
    db: Session = Depends(get_db),
    admin_user: User = Depends(
        require_admin,
    ),
):
    total_users = (
        db.query(func.count(User.id))
        .scalar()
        or 0
    )

    active_users = (
        db.query(func.count(User.id))
        .filter(User.is_active.is_(True))
        .scalar()
        or 0
    )

    pro_users = (
        db.query(func.count(User.id))
        .filter(User.plan == "pro")
        .scalar()
        or 0
    )

    premium_users = (
        db.query(func.count(User.id))
        .filter(User.plan == "premium")
        .scalar()
        or 0
    )

    active_subscriptions = (
        db.query(
            func.count(Subscription.id)
        )
        .filter(
            Subscription.status == "active"
        )
        .scalar()
        or 0
    )

    pending_subscriptions = (
        db.query(
            func.count(Subscription.id)
        )
        .filter(
            Subscription.status
            == "approval_pending"
        )
        .scalar()
        or 0
    )

    total_trades = (
        db.query(func.count(Trade.id))
        .scalar()
        or 0
    )

    return {
        "admin": {
            "id": admin_user.id,
            "email": admin_user.email,
        },
        "users": {
            "total": total_users,
            "active": active_users,
            "pro": pro_users,
            "premium": premium_users,
        },
        "subscriptions": {
            "active": active_subscriptions,
            "pending": pending_subscriptions,
        },
        "trades": {
            "total": total_trades,
        },
        "system": {
            "status": "healthy",
        },
    }
