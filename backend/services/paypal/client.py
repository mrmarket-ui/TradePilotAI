from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()


class PayPalConfigurationError(RuntimeError):
    pass


class PayPalAPIError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details


def get_paypal_base_url() -> str:
    environment = (
        os.getenv("PAYPAL_ENV", "sandbox")
        .strip()
        .lower()
    )

    if environment == "sandbox":
        return "https://api-m.sandbox.paypal.com"

    if environment == "live":
        return "https://api-m.paypal.com"

    raise PayPalConfigurationError(
        "PAYPAL_ENV must be either 'sandbox' or 'live'."
    )


def get_paypal_credentials() -> tuple[str, str]:
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    secret = os.getenv("PAYPAL_SECRET")

    if not client_id or not secret:
        raise PayPalConfigurationError(
            "PAYPAL_CLIENT_ID and PAYPAL_SECRET must be configured."
        )

    return client_id, secret


def get_access_token() -> str:
    client_id, secret = get_paypal_credentials()

    try:
        response = httpx.post(
            f"{get_paypal_base_url()}/v1/oauth2/token",
            auth=(client_id, secret),
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Content-Type":
                    "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "client_credentials",
            },
            timeout=20.0,
        )
    except httpx.HTTPError as exc:
        raise PayPalAPIError(
            "Could not connect to PayPal.",
            details=str(exc),
        ) from exc

    if response.status_code != 200:
        try:
            details = response.json()
        except ValueError:
            details = response.text

        raise PayPalAPIError(
            "PayPal rejected the access-token request.",
            status_code=response.status_code,
            details=details,
        )

    payload = response.json()
    access_token = payload.get("access_token")

    if not access_token:
        raise PayPalAPIError(
            "PayPal returned no access token.",
            details=payload,
        )

    return str(access_token)


def paypal_request(
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    token = get_access_token()

    request_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if headers:
        request_headers.update(headers)

    try:
        response = httpx.request(
            method=method,
            url=f"{get_paypal_base_url()}{path}",
            headers=request_headers,
            json=json,
            timeout=30.0,
        )
    except httpx.HTTPError as exc:
        raise PayPalAPIError(
            "Could not connect to PayPal.",
            details=str(exc),
        ) from exc

    if response.status_code >= 400:
        try:
            details = response.json()
        except ValueError:
            details = response.text

        raise PayPalAPIError(
            "PayPal API request failed.",
            status_code=response.status_code,
            details=details,
        )

    if response.status_code == 204:
        return {}

    return response.json()
