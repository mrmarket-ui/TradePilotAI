from datetime import datetime

import main

from database.database import SessionLocal
from models.subscription import Subscription
from models.user import User
from services.paypal.client import paypal_request
from services.subscriptions.plans import get_subscription_plans


subscription_id = "I-KMM6E9TXEK80"
user_id = 1

paypal_data = paypal_request(
    "GET",
    f"/v1/billing/subscriptions/{subscription_id}",
)

print("PAYPAL STATUS:", paypal_data.get("status"))
print("PAYPAL PLAN:", paypal_data.get("plan_id"))

if paypal_data.get("status") != "ACTIVE":
    raise RuntimeError(
        "The selected PayPal subscription is not ACTIVE."
    )

plans = get_subscription_plans()

plan = next(
    (
        item
        for item in plans.values()
        if item.paypal_plan_id
        == paypal_data.get("plan_id")
    ),
    None,
)

if plan is None:
    raise RuntimeError(
        "The PayPal plan ID does not match Pro or Premium."
    )

db = SessionLocal()

try:
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id
        )
        .first()
    )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if subscription is None or user is None:
        raise RuntimeError(
            "User or subscription record was not found."
        )

    billing_info = paypal_data.get(
        "billing_info",
        {},
    )

    subscriber = paypal_data.get(
        "subscriber",
        {},
    )

    next_billing = billing_info.get(
        "next_billing_time"
    )

    subscription.paypal_subscription_id = (
        subscription_id
    )
    subscription.paypal_plan_id = (
        plan.paypal_plan_id
    )
    subscription.plan = plan.code
    subscription.status = "active"
    subscription.amount = plan.amount
    subscription.currency = plan.currency
    subscription.payer_email = (
        subscriber.get("email_address")
        or subscription.payer_email
    )
    subscription.paypal_payer_id = (
        subscriber.get("payer_id")
        or subscription.paypal_payer_id
    )

    if next_billing:
        subscription.next_billing_at = (
            datetime.fromisoformat(
                next_billing.replace(
                    "Z",
                    "+00:00",
                )
            )
        )

    user.plan = plan.code
    user.ai_credits = max(
        user.ai_credits or 0,
        plan.ai_credits,
    )

    db.commit()

    print("LOCAL PLAN:", user.plan)
    print("LOCAL STATUS:", subscription.status)
    print("AI CREDITS:", user.ai_credits)

finally:
    db.close()
