"""
TradePilot AI token-signing settings.

The signing key must come from the environment (backend/.env locally, the
host's secret store in production). It must never be written into the code:
anyone who can read the code could then create valid login tokens.
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MIN_SECRET_LENGTH = 32


def _required_secret() -> str:
    key = os.getenv("SECRET_KEY", "").strip()

    if len(key) < MIN_SECRET_LENGTH:
        raise RuntimeError(
            "SECRET_KEY is missing or too short. Set it in backend/.env to a "
            "random value of at least 32 characters, for example: "
            'python -c "import secrets; print(secrets.token_urlsafe(64))"'
        )

    return key


def _expire_minutes() -> int:
    try:
        minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    except ValueError:
        minutes = 60

    return min(max(minutes, 5), 1440)


SECRET_KEY = _required_secret()

# Fixed on purpose and never read from the environment, so nobody can switch
# verification to a weaker algorithm.
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = _expire_minutes()

ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)