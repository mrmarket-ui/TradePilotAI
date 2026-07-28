from fastapi import (
    Depends,
    HTTPException,
    status,
)

from dependencies.auth import get_current_user
from models.user import User


PAID_PLANS = {
    "pro",
    "premium",
}


def require_paid_plan(
    current_user: User = Depends(
        get_current_user,
    ),
) -> User:
    plan = (
        current_user.plan
        or "free"
    ).strip().lower()

    if plan not in PAID_PLANS:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail={
                "code": "UPGRADE_REQUIRED",
                "message": (
                    "This feature requires "
                    "TradePilot AI Pro or Premium."
                ),
                "current_plan": plan,
                "required_plans": [
                    "pro",
                    "premium",
                ],
            },
        )

    return current_user


def require_premium_plan(
    current_user: User = Depends(
        get_current_user,
    ),
) -> User:
    plan = (
        current_user.plan
        or "free"
    ).strip().lower()

    if plan != "premium":
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail={
                "code": (
                    "PREMIUM_UPGRADE_REQUIRED"
                ),
                "message": (
                    "This feature requires "
                    "TradePilot AI Premium."
                ),
                "current_plan": plan,
                "required_plans": [
                    "premium",
                ],
            },
        )

    return current_user
