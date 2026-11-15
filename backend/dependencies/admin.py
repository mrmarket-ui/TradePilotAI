import os

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from dependencies.auth import get_current_user
from models.user import User


def require_active_user(
    current_user: User = Depends(
        get_current_user,
    ),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCOUNT_INACTIVE",
                "message": (
                    "This account has been "
                    "suspended or deactivated."
                ),
            },
        )

    return current_user


def _is_production() -> bool:
    return os.getenv("APP_ENV", "development").strip().lower() == "production"


def _admin_allowed(user: User) -> bool:
    """
    Only the owner may use the admin area.

    OWNER_EMAIL names the one account allowed in. In production it is
    required: if it is missing, nobody gets in (fail closed). In development
    it is optional, and without it any account marked as admin is accepted.
    """

    if not user.is_admin:
        return False

    owner = os.getenv("OWNER_EMAIL", "").strip().lower()
    is_owner = bool(owner) and (user.email or "").strip().lower() == owner

    if _is_production():
        return is_owner

    return is_owner or not owner


def require_admin(
    current_user: User = Depends(
        require_active_user,
    ),
) -> User:
    if not _admin_allowed(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ADMIN_REQUIRED",
                "message": (
                    "Administrator access "
                    "is required."
                ),
            },
        )

    return current_user
