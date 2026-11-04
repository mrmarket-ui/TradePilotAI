"""
TradePilot AI one-time codes.

Used for the email code that completes every login.

Design choices
--------------
* 6 digits (1 guess in 1,000,000) instead of 4 (1 in 10,000).
* Codes come from the operating system's secure random source.
* Only an HMAC of the code is stored, keyed with the server secret, so a copy
  of the database alone cannot be brute-forced offline.
* Codes expire quickly and allow only a few wrong guesses.
* Everything here is pure (no database, no network) so it is easy to test.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

OTP_LENGTH = 6
OTP_TTL_MINUTES = 10
OTP_MAX_ATTEMPTS = 5
OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_MAX_RESENDS = 3

MIN_SECRET_LENGTH = 32


def utc_now() -> datetime:
    """Naive UTC time, matching the rest of the database."""

    return datetime.now(timezone.utc).replace(tzinfo=None)


def secret_key_problem() -> str | None:
    key = os.getenv("SECRET_KEY", "")

    if not key:
        return "SECRET_KEY is not set."

    if len(key) < MIN_SECRET_LENGTH:
        return f"SECRET_KEY is shorter than {MIN_SECRET_LENGTH} characters."

    return None


def _secret_key() -> bytes:
    key = os.getenv("SECRET_KEY", "")

    if not key:
        raise RuntimeError("SECRET_KEY is not configured.")

    return key.encode("utf-8")


def new_challenge_id() -> str:
    return secrets.token_urlsafe(32)


def generate_code(length: int = OTP_LENGTH) -> str:
    return "".join(secrets.choice("0123456789") for _ in range(length))


def clean_code(submitted: object) -> str:
    """Keep digits only, so '123 456' and '123-456' are accepted."""

    return "".join(ch for ch in str(submitted or "") if ch.isdigit())


def hash_code(code: str, challenge_id: str) -> str:
    message = f"{challenge_id}:{code}".encode("utf-8")

    return hmac.new(_secret_key(), message, hashlib.sha256).hexdigest()


def code_matches(submitted: object, challenge_id: str, expected_hash: str) -> bool:
    cleaned = clean_code(submitted)

    candidate = hash_code(cleaned, challenge_id)

    same = hmac.compare_digest(candidate, expected_hash or "")

    return same and len(cleaned) == OTP_LENGTH


def expiry_time(now: datetime | None = None) -> datetime:
    return (now or utc_now()) + timedelta(minutes=OTP_TTL_MINUTES)


def is_expired(expires_at: datetime, now: datetime | None = None) -> bool:
    return (now or utc_now()) >= expires_at


def check_attempt(
    *,
    submitted: object,
    challenge_id: str,
    code_hash: str,
    expires_at: datetime,
    attempts: int,
    consumed_at: datetime | None,
    now: datetime | None = None,
) -> str:
    """
    Returns one of: "ok", "wrong", "expired", "locked", "used".

    The caller is responsible for adding 1 to the attempt counter on "wrong"
    and for marking the challenge consumed on "ok".
    """

    current = now or utc_now()

    if consumed_at is not None:
        return "used"

    if attempts >= OTP_MAX_ATTEMPTS:
        return "locked"

    if is_expired(expires_at, current):
        return "expired"

    if code_matches(submitted, challenge_id, code_hash):
        return "ok"

    return "wrong"


def resend_allowed(
    *,
    last_sent_at: datetime,
    resend_count: int,
    now: datetime | None = None,
) -> tuple[bool, int]:
    """Returns (allowed, seconds_to_wait). A wait of 0 with allowed=False
    means the resend limit for this challenge has been used up."""

    current = now or utc_now()

    if resend_count >= OTP_MAX_RESENDS:
        return False, 0

    ready_at = last_sent_at + timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS)

    if current < ready_at:
        return False, max(1, int((ready_at - current).total_seconds()))

    return True, 0


def mask_email(email: str) -> str:
    local, _, domain = (email or "").partition("@")

    if not local or not domain:
        return "your email"

    return f"{local[0]}***@{domain}"