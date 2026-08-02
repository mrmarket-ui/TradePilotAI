from __future__ import annotations

import uuid
from typing import Any

from services.paypal.client import (
    paypal_request,
)

from services.subscriptions.plans import (
    SubscriptionPlan,
)


def _find_approval_url(
    paypal_response: dict[str, Any],
) -> str:
    for link in paypal_response.get(
        "links",
        [],
    ):
        if link.get("rel") in {
            "approve",
            "payer-action",
        }:
            href = link.get("href")

            if href:
                return str(href)

    raise RuntimeError(
        "PayPal returned no approval URL."
    )


def create_paypal_subscription(
    *,
    user_id: int,
    user_email: str,
    plan: SubscriptionPlan,
) -> dict[str, str]:
    response = paypal_request(
        "POST",
        "/v1/billing/subscriptions",
        headers={
            "PayPal-Request-Id": (
                "tradepilot-subscription-"
                f"{uuid.uuid4()}"
            ),
            "Prefer": "return=representation",
        },
        json={
            "plan_id": plan.paypal_plan_id,
            "custom_id": (
                f"tradepilot-user-{user_id}"
            ),
            "subscriber": {
                "email_address": user_email,
            },
        },
    )

    subscription_id = response.get("id")
    status = response.get(
        "status",
        "APPROVAL_PENDING",
    )

    if not subscription_id:
        raise RuntimeError(
            "PayPal returned no subscription ID."
        )

    return {
        "subscription_id": str(
            subscription_id
        ),
        "status": str(status),
        "approval_url": (
            _find_approval_url(response)
        ),
    }
def cancel_paypal_subscription(
    paypal_subscription_id: str,
    reason: str = (
        "Customer requested cancellation "
        "through TradePilot AI."
    ),
) -> None:
    """
    Cancel an existing PayPal subscription.

    This stops future recurring billing.
    """
    if not paypal_subscription_id:
        raise ValueError(
            "PayPal subscription ID is required."
        )

    paypal_request(
        "POST",
        (
            "/v1/billing/subscriptions/"
            f"{paypal_subscription_id}/cancel"
        ),
        json={
            "reason": reason,
        },
    )
