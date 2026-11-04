"""
TradePilot AI single-use tokens (password-reset links).

The raw token is only ever sent by email. The database stores a SHA-256 hash,
so a copy of the database cannot be used to reset anyone's password. The token
carries 256 bits of randomness, so a plain hash is safe here.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets

RESET_TOKEN_TTL_MINUTES = 30

_TOKEN_SHAPE = re.compile(r"^[A-Za-z0-9_-]{40,64}$")


def new_token() -> tuple[str, str]:
    """Returns (raw_token_for_the_email, hash_to_store)."""

    raw = secrets.token_urlsafe(32)

    return raw, hash_token(raw)


def hash_token(raw: str) -> str:
    return hashlib.sha256(str(raw or "").encode("utf-8")).hexdigest()


def is_plausible_token(raw: object) -> bool:
    return isinstance(raw, str) and bool(_TOKEN_SHAPE.match(raw))


def token_matches(raw: object, stored_hash: str) -> bool:
    if not is_plausible_token(raw):
        return False

    return hmac.compare_digest(hash_token(str(raw)), stored_hash or "")