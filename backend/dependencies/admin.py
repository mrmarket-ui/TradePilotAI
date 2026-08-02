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


def require_admin(
    current_user: User = Depends(
        require_active_user,
    ),
) -> User:
    if not current_user.is_admin:
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
