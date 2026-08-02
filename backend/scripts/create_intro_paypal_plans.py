import os

from dotenv import load_dotenv

from services.paypal.client import paypal_request


load_dotenv(override=True)


product_id = os.getenv("PAYPAL_PRODUCT_ID")

if not product_id:
    raise RuntimeError(
        "PAYPAL_PRODUCT_ID is not configured."
    )


def create_plan(
    name: str,
    description: str,
    regular_price: str,
):
    payload = {
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
                "tenure_type": "TRIAL",
                "sequence": 1,
                "total_cycles": 1,
                "pricing_scheme": {
                    "fixed_price": {
                        "value": "10.00",
                        "currency_code": "USD",
                    }
                },
            },
            {
                "frequency": {
                    "interval_unit": "MONTH",
                    "interval_count": 1,
                },
                "tenure_type": "REGULAR",
                "sequence": 2,
                "total_cycles": 0,
                "pricing_scheme": {
                    "fixed_price": {
                        "value": regular_price,
                        "currency_code": "USD",
                    }
                },
            },
        ],
        "payment_preferences": {
            "auto_bill_outstanding": True,
            "payment_failure_threshold": 1,
        },
    }

    result = paypal_request(
        "POST",
        "/v1/billing/plans",
        json=payload,
    )

    return result


pro = create_plan(
    name="TradePilot AI Pro",
    description=(
        "$10 first month, then "
        "$19.99 USD per month."
    ),
    regular_price="19.99",
)

premium = create_plan(
    name="TradePilot AI Premium",
    description=(
        "$10 first month, then "
        "$29.99 USD per month."
    ),
    regular_price="29.99",
)


print()
print("NEW PRO PLAN ID:")
print(pro.get("id"))

print()
print("NEW PREMIUM PLAN ID:")
print(premium.get("id"))

print()
print("PRO STATUS:")
print(pro.get("status"))

print()
print("PREMIUM STATUS:")
print(premium.get("status"))
