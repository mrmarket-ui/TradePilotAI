from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class SubscriptionPlan:
    code: str
    name: str
    paypal_plan_id: str
    amount: str
    currency: str
    ai_credits: int


def _required_environment(
    variable_name: str,
) -> str:
    value = os.getenv(variable_name)

    if not value:
        raise RuntimeError(
            f"{variable_name} is not configured."
        )

    return value


def get_subscription_plans() -> dict[
    str,
    SubscriptionPlan,
]:
    return {
        "pro": SubscriptionPlan(
            code="pro",
            name="TradePilot AI Pro",
            paypal_plan_id=(
                _required_environment(
                    "PAYPAL_PRO_PLAN_ID"
                )
            ),
            amount="19.99",
            currency="USD",
            ai_credits=500,
        ),
        "premium": SubscriptionPlan(
            code="premium",
            name="TradePilot AI Premium",
            paypal_plan_id=(
                _required_environment(
                    "PAYPAL_PREMIUM_PLAN_ID"
                )
            ),
            amount="29.99",
            currency="USD",
            ai_credits=1500,
        ),
    }


def get_subscription_plan(
    plan_code: str,
) -> SubscriptionPlan:
    clean_code = plan_code.strip().lower()
    plans = get_subscription_plans()

    if clean_code not in plans:
        raise ValueError(
            "Plan must be 'pro' or 'premium'."
        )

    return plans[clean_code]
