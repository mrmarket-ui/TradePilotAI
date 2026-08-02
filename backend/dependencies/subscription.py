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


def has_admin_access(
    user: User,
) -> bool:
    """
    Platform administrators receive full feature access
    without requiring a paid subscription.

    This does NOT create or modify PayPal subscriptions.
    """
    return bool(user.is_admin)


def require_paid_plan(
    current_user: User = Depends(
        get_current_user,
    ),
) -> User:

    # -------------------------------------------------
    # ADMIN / OWNER BYPASS
    # -------------------------------------------------
    if has_admin_access(current_user):
        return current_user

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

    # -------------------------------------------------
    # ADMIN / OWNER BYPASS
    # -------------------------------------------------
    if has_admin_access(current_user):
        return current_user

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
