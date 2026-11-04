"""
TradePilot AI password rules.

Follows current guidance: a sensible minimum length and a block-list of
obvious passwords, instead of forcing symbols. The 72-byte ceiling exists
because bcrypt ignores everything after 72 bytes, which would let two
different long passwords look identical.
"""

from __future__ import annotations

MIN_LENGTH = 10
MAX_BYTES = 72

_COMMON = {
    "password", "password1", "password123", "passw0rd", "letmein", "letmein123",
    "welcome", "welcome1", "welcome123", "qwerty", "qwertyuiop", "qwerty123",
    "iloveyou", "admin", "admin123", "administrator", "trading", "trader",
    "trader123", "forex", "forex123", "tradepilot", "tradepilotai",
    "tradepilot123", "mrmarket", "mrmarket123", "abc123", "abcd1234",
    "monkey", "dragon", "football", "baseball", "1q2w3e4r", "zxcvbnm",
}


_SEQUENCES = (
    "01234567890123456789",
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiopasdfghjklzxcvbnm",
)


def _is_sequence(value: str) -> bool:
    if len(value) < 6:
        return False

    if len(set(value)) == 1:
        return True

    return any(value in seq or value in seq[::-1] for seq in _SEQUENCES)


def validate_password(password: str, email: str = "") -> list[str]:
    """Returns a list of problems. An empty list means the password is fine."""

    problems: list[str] = []
    value = password or ""
    lowered = value.lower()

    if len(value) < MIN_LENGTH:
        problems.append(f"Use at least {MIN_LENGTH} characters.")

    if len(value.encode("utf-8")) > MAX_BYTES:
        problems.append("Use at most 72 bytes (about 72 characters).")

    if lowered.strip() in _COMMON or lowered.rstrip("0123456789!") in _COMMON:
        problems.append("That password is too common.")

    if _is_sequence(lowered):
        problems.append("Avoid repeated or sequential characters.")

    local = (email or "").split("@")[0].lower()

    if len(local) >= 4 and local in lowered:
        problems.append("Do not include your email name in your password.")

    return problems