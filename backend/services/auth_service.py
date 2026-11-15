"""
Password hashing.

PBKDF2-SHA256 with 600,000 rounds (the current OWASP guidance). Accounts
created with the older, weaker setting keep working: verify_and_update() hands
back a stronger hash the next time the person signs in, and the caller saves it.
"""

from passlib.context import CryptContext

PBKDF2_ROUNDS = 600_000

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=PBKDF2_ROUNDS,
    pbkdf2_sha256__min_rounds=PBKDF2_ROUNDS,
)

_dummy_hash: str | None = None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        return False


def verify_and_update(
    plain_password: str,
    hashed_password: str,
) -> tuple[bool, str | None]:
    """Returns (is_correct, new_hash_to_store_or_None)."""

    try:
        return pwd_context.verify_and_update(plain_password, hashed_password)
    except ValueError:
        return False, None


def burn_password_time(password: str) -> None:
    """Spend the same time as a real check, so an unknown email cannot be
    told apart from a wrong password by how long the answer takes."""

    global _dummy_hash

    if _dummy_hash is None:
        _dummy_hash = pwd_context.hash("tradepilot-timing-placeholder")

    try:
        pwd_context.verify(password, _dummy_hash)
    except ValueError:
        pass
