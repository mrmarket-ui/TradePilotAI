from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from models.paypal_webhook_event import (
    PayPalWebhookEvent,
)
from models.subscription import Subscription
from models.user import User

from services.subscriptions.plans import (
    get_subscription_plans,
)


ACTIVE_EVENTS = {
    "BILLING.SUBSCRIPTION.ACTIVATED",
}

CANCELLED_EVENTS = {
    "BILLING.SUBSCRIPTION.CANCELLED",
}

SUSPENDED_EVENTS = {
    "BILLING.SUBSCRIPTION.SUSPENDED",
    "BILLING.SUBSCRIPTION.PAYMENT.FAILED",
}

EXPIRED_EVENTS = {
    "BILLING.SUBSCRIPTION.EXPIRED",
}

PAYMENT_COMPLETED_EVENTS = {
    "PAYMENT.SALE.COMPLETED",
}

PAYMENT_REVERSED_EVENTS = {
    "PAYMENT.SALE.REFUNDED",
    "PAYMENT.SALE.REVERSED",
}


def parse_paypal_datetime(
    value: Any,
) -> datetime | None:
    if not value or not isinstance(
        value,
        str,
    ):
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return None


def get_existing_event(
    db: Session,
    paypal_event_id: str,
) -> PayPalWebhookEvent | None:
    return (
        db.query(PayPalWebhookEvent)
        .filter(
            PayPalWebhookEvent
            .paypal_event_id
            == paypal_event_id
        )
        .first()
    )


def create_event_record(
    db: Session,
    event: dict[str, Any],
) -> PayPalWebhookEvent:
    resource = event.get("resource") or {}

    record = PayPalWebhookEvent(
        paypal_event_id=str(event["id"]),
        event_type=str(
            event.get("event_type", "")
        ),
        resource_id=(
            str(resource.get("id"))
            if resource.get("id")
            else None
        ),
        processing_status="received",
        payload=event,
    )

    db.add(record)
    db.flush()

    return record


def find_subscription(
    db: Session,
    resource: dict[str, Any],
) -> Subscription | None:
    resource_id = resource.get("id")

    if resource_id:
        direct_match = (
            db.query(Subscription)
            .filter(
                Subscription
                .paypal_subscription_id
                == str(resource_id)
            )
            .first()
        )

        if direct_match:
            return direct_match

    billing_agreement_id = (
        resource.get(
            "billing_agreement_id"
        )
    )

    if billing_agreement_id:
        return (
            db.query(Subscription)
            .filter(
                Subscription
                .paypal_subscription_id
                == str(
                    billing_agreement_id
                )
            )
            .first()
        )

    return None


def plan_from_paypal_plan_id(
    paypal_plan_id: str | None,
) -> str | None:
    if not paypal_plan_id:
        return None

    for plan in (
        get_subscription_plans()
        .values()
    ):
        if (
            plan.paypal_plan_id
            == paypal_plan_id
        ):
            return plan.code

    return None


def apply_active_subscription(
    db: Session,
    subscription: Subscription,
    resource: dict[str, Any],
) -> None:
    paypal_plan_id = (
        resource.get("plan_id")
        or subscription.paypal_plan_id
    )

    plan_code = (
        plan_from_paypal_plan_id(
            str(paypal_plan_id)
            if paypal_plan_id
            else None
        )
        or subscription.plan
    )

    plan = get_subscription_plans().get(
        plan_code
    )

    subscription.plan = plan_code
    subscription.status = "active"

    if paypal_plan_id:
        subscription.paypal_plan_id = str(
            paypal_plan_id
        )

    billing_info = (
        resource.get("billing_info")
        or {}
    )

    subscription.next_billing_at = (
        parse_paypal_datetime(
            billing_info.get(
                "next_billing_time"
            )
        )
    )

    subscriber = (
        resource.get("subscriber")
        or {}
    )

    subscription.paypal_payer_id = (
        subscriber.get("payer_id")
        or subscription.paypal_payer_id
    )

    subscription.payer_email = (
        subscriber.get("email_address")
        or subscription.payer_email
    )

    user = (
        db.query(User)
        .filter(
            User.id
            == subscription.user_id
        )
        .first()
    )

    if user:
        user.plan = plan_code

        if plan:
            user.ai_credits = max(
                user.ai_credits or 0,
                plan.ai_credits,
            )


def apply_subscription_status(
    subscription: Subscription,
    status: str,
) -> None:
    subscription.status = status

    if status == "cancelled":
        subscription.cancelled_at = (
            datetime.utcnow()
        )


def process_paypal_event(
    db: Session,
    event: dict[str, Any],
) -> dict[str, Any]:
    paypal_event_id = event.get("id")
    event_type = event.get("event_type")
    resource = event.get("resource") or {}

    if not paypal_event_id:
        raise ValueError(
            "PayPal event has no ID."
        )

    if not event_type:
        raise ValueError(
            "PayPal event has no type."
        )

    existing = get_existing_event(
        db=db,
        paypal_event_id=str(
            paypal_event_id
        ),
    )

    if existing:
        return {
            "processed": False,
            "duplicate": True,
            "event_id":
                str(paypal_event_id),
        }

    record = create_event_record(
        db=db,
        event=event,
    )

    try:
        subscription = find_subscription(
            db=db,
            resource=resource,
        )

        if subscription is None:
            record.processing_status = (
                "ignored"
            )
            record.error_message = (
                "No matching subscription."
            )
            record.processed_at = (
                datetime.utcnow()
            )
            db.commit()

            return {
                "processed": False,
                "duplicate": False,
                "ignored": True,
                "event_id":
                    str(paypal_event_id),
            }

        if event_type in ACTIVE_EVENTS:
            apply_active_subscription(
                db=db,
                subscription=subscription,
                resource=resource,
            )

        elif event_type in CANCELLED_EVENTS:
            apply_subscription_status(
                subscription,
                "cancelled",
            )

        elif event_type in SUSPENDED_EVENTS:
            apply_subscription_status(
                subscription,
                "suspended",
            )

        elif event_type in EXPIRED_EVENTS:
            apply_subscription_status(
                subscription,
                "expired",
            )

        elif (
            event_type
            in PAYMENT_COMPLETED_EVENTS
        ):
            subscription.last_payment_at = (
                parse_paypal_datetime(
                    event.get("create_time")
                )
                or datetime.utcnow()
            )

            subscription.status = "active"

        elif (
            event_type
            in PAYMENT_REVERSED_EVENTS
        ):
            subscription.status = (
                "suspended"
            )

        else:
            record.processing_status = (
                "ignored"
            )
            record.processed_at = (
                datetime.utcnow()
            )
            db.commit()

            return {
                "processed": False,
                "duplicate": False,
                "ignored": True,
                "event_id":
                    str(paypal_event_id),
            }

        record.processing_status = (
            "processed"
        )
        record.processed_at = (
            datetime.utcnow()
        )

        db.commit()

        return {
            "processed": True,
            "duplicate": False,
            "event_id":
                str(paypal_event_id),
            "event_type":
                str(event_type),
        }

    except Exception as exc:
        db.rollback()

        failed_record = (
            db.query(PayPalWebhookEvent)
            .filter(
                PayPalWebhookEvent
                .paypal_event_id
                == str(paypal_event_id)
            )
            .first()
        )

        if failed_record:
            failed_record.processing_status = (
                "failed"
            )
            failed_record.error_message = (
                str(exc)[:1000]
            )
            failed_record.processed_at = (
                datetime.utcnow()
            )
            db.commit()

        raise
