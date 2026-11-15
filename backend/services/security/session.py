"""
Turns a login token into a user, with every check in one place.

A token is only accepted if the user still exists, is active, and the token
carries the user's current session version. Resetting a password or choosing
"sign out everywhere" raises that version, which ends every older session.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.auth_security import AuthSecurity
from models.user import User
from services.jwt_service import verify_token


def _unauthorised(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def resolve_user(db: Session, token: str) -> User:
    payload = verify_token(token)

    if payload is None:
        raise _unauthorised("Could not validate credentials")

    user_id = payload.get("id")
    version = payload.get("tv")

    if (
        not isinstance(user_id, int)
        or isinstance(user_id, bool)
        or not isinstance(version, int)
        or isinstance(version, bool)
    ):
        raise _unauthorised("Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise _unauthorised("Could not validate credentials")

    security = (
        db.query(AuthSecurity).filter(AuthSecurity.user_id == user_id).first()
    )

    current = security.token_version if security is not None else 0

    if version != current:
        raise _unauthorised("Your session has ended. Please sign in again.")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCOUNT_INACTIVE",
                "message": "This account has been suspended or deactivated.",
            },
        )

    return user
