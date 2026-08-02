from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.admin import require_admin

from models.subscription import Subscription
from models.user import User


router = APIRouter(
    prefix="/admin/subscriptions",
    tags=["Admin Subscriptions"],
)


@router.get("")
def list_admin_subscriptions(
    status_filter: str | None = Query(
        default=None,
        alias="status",
        max_length=40,
    ),
    plan: str | None = Query(
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
    query = db.query(Subscription)

    if status_filter:
        query = query.filter(
            Subscription.status
            == status_filter.strip().lower()
        )

    if plan:
        query = query.filter(
            Subscription.plan
            == plan.strip().lower()
        )

    total = query.count()

    subscriptions = (
        query
        .order_by(
            Subscription.created_at.desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "subscriptions": [
            {
                "id": item.id,
                "user_id": item.user_id,
                "provider": item.provider,
                "plan": item.plan,
                "status": item.status,
                "paypal_subscription_id":
                    item.paypal_subscription_id,
                "paypal_plan_id":
                    item.paypal_plan_id,
                "paypal_payer_id":
                    item.paypal_payer_id,
                "payer_email":
                    item.payer_email,
                "currency":
                    item.currency,
                "amount":
                    item.amount,
                "current_period_start":
                    item.current_period_start,
                "current_period_end":
                    item.current_period_end,
                "next_billing_at":
                    item.next_billing_at,
                "cancelled_at":
                    item.cancelled_at,
                "last_payment_at":
                    item.last_payment_at,
                "created_at":
                    item.created_at,
                "updated_at":
                    item.updated_at,
            }
            for item in subscriptions
        ],
    }
