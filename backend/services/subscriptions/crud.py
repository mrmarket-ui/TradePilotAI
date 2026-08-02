from sqlalchemy.orm import Session

from models.subscription import Subscription
from models.user import User

from services.subscriptions.plans import (
    SubscriptionPlan,
)


def get_subscription(
    db: Session,
    user_id: int,
) -> Subscription | None:
    return (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id
        )
        .first()
    )


def create_free_subscription(
    db: Session,
    user_id: int,
) -> Subscription:
    subscription = Subscription(
        user_id=user_id,
        provider="paypal",
        plan="free",
        status="inactive",
        currency="USD",
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


def get_or_create_subscription(
    db: Session,
    user_id: int,
) -> Subscription:
    existing = get_subscription(
        db=db,
        user_id=user_id,
    )

    if existing is not None:
        return existing

    return create_free_subscription(
        db=db,
        user_id=user_id,
    )


def save_pending_paypal_subscription(
    db: Session,
    user: User,
    plan: SubscriptionPlan,
    paypal_subscription_id: str,
    paypal_status: str,
) -> Subscription:
    subscription = get_or_create_subscription(
        db=db,
        user_id=user.id,
    )

    subscription.provider = "paypal"
    subscription.plan = plan.code
    subscription.status = (
        paypal_status.strip().lower()
    )

    subscription.paypal_subscription_id = (
        paypal_subscription_id
    )

    subscription.paypal_plan_id = (
        plan.paypal_plan_id
    )

    subscription.payer_email = user.email
    subscription.currency = plan.currency
    subscription.amount = plan.amount

    db.commit()
    db.refresh(subscription)

    return subscription

def mark_subscription_cancelled(
    db: Session,
    subscription: Subscription,
) -> Subscription:
    subscription.status = "cancelled"

    db.commit()
    db.refresh(subscription)

    return subscription
