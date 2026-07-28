from __future__ import annotations

import os
from typing import Any, Mapping

from dotenv import load_dotenv

from services.paypal.client import (
    PayPalConfigurationError,
    paypal_request,
)


load_dotenv()


REQUIRED_PAYPAL_HEADERS = {
    "transmission_id":
        "paypal-transmission-id",
    "transmission_time":
        "paypal-transmission-time",
    "transmission_sig":
        "paypal-transmission-sig",
    "cert_url":
        "paypal-cert-url",
    "auth_algo":
        "paypal-auth-algo",
}


def get_webhook_id() -> str:
    webhook_id = os.getenv(
        "PAYPAL_WEBHOOK_ID"
    )

    if not webhook_id:
        raise PayPalConfigurationError(
            "PAYPAL_WEBHOOK_ID is not configured."
        )

    return webhook_id


def extract_verification_headers(
    headers: Mapping[str, str],
) -> dict[str, str]:
    extracted: dict[str, str] = {}

    for field, header_name in (
        REQUIRED_PAYPAL_HEADERS.items()
    ):
        value = headers.get(header_name)

        if not value:
            raise ValueError(
                f"Missing PayPal header: "
                f"{header_name}"
            )

        extracted[field] = value

    return extracted


def verify_webhook_signature(
    *,
    headers: Mapping[str, str],
    event: dict[str, Any],
) -> bool:
    verification_headers = (
        extract_verification_headers(
            headers
        )
    )

    result = paypal_request(
        "POST",
        (
            "/v1/notifications/"
            "verify-webhook-signature"
        ),
        json={
            **verification_headers,
            "webhook_id":
                get_webhook_id(),
            "webhook_event": event,
        },
    )

    return (
        str(
            result.get(
                "verification_status",
                "",
            )
        ).upper()
        == "SUCCESS"
    )
