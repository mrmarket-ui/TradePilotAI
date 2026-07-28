from __future__ import annotations

import os
import uuid

from dotenv import load_dotenv

from services.paypal.client import paypal_request


load_dotenv()


def create_product() -> dict:
    return paypal_request(
        "POST",
        "/v1/catalogs/products",
        headers={
            "PayPal-Request-Id":
                f"tradepilot-product-{uuid.uuid4()}",
            "Prefer": "return=representation",
        },
        json={
            "name": "TradePilot AI Membership",
            "description": (
                "Recurring access to TradePilot AI "
                "trading intelligence features."
            ),
            "type": "SERVICE",
            "category": "SOFTWARE",
        },
    )


def create_plan(
    *,
    product_id: str,
    name: str,
    description: str,
    price: str,
) -> dict:
    return paypal_request(
        "POST",
        "/v1/billing/plans",
        headers={
            "PayPal-Request-Id":
                f"tradepilot-plan-{uuid.uuid4()}",
            "Prefer": "return=representation",
        },
        json={
            "product_id": product_id,
            "name": name,
            "description": description,
            "status": "ACTIVE",
            "billing_cycles": [
                {
                    "frequency": {
                        "interval_unit": "MONTH",
                        "interval_count": 1,
                    },
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": price,
                            "currency_code": "USD",
                        }
                    },
                }
            ],
            "payment_preferences": {
                "auto_bill_outstanding": True,
                "setup_fee_failure_action":
                    "CONTINUE",
                "payment_failure_threshold": 1,
            },
        },
    )


def main() -> None:
    environment = os.getenv(
        "PAYPAL_ENV",
        "sandbox",
    ).lower()

    if environment != "sandbox":
        raise RuntimeError(
            "This setup script is restricted to "
            "PAYPAL_ENV=sandbox."
        )

    product = create_product()
    product_id = product["id"]

    pro = create_plan(
        product_id=product_id,
        name="TradePilot AI Pro",
        description=(
            "Unlimited trade journalling, "
            "Strategy Brain, Setup Scorer, "
            "AI Coach and advanced reports."
        ),
        price="19.99",
    )

    premium = create_plan(
        product_id=product_id,
        name="TradePilot AI Premium",
        description=(
            "Everything in Pro plus premium "
            "AI analysis, advanced Trader DNA "
            "and future Vision AI capabilities."
        ),
        price="29.99",
    )

    print()
    print("PayPal Sandbox resources created.")
    print()
    print(
        "PAYPAL_PRODUCT_ID="
        f"{product_id}"
    )
    print(
        "PAYPAL_PRO_PLAN_ID="
        f"{pro['id']}"
    )
    print(
        "PAYPAL_PREMIUM_PLAN_ID="
        f"{premium['id']}"
    )
    print()
    print(
        "Copy these IDs into the backend "
        "and frontend environment files."
    )


if __name__ == "__main__":
    main()
