from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.profile_schema import ProfileResponse
from schemas.update_profile import UpdateProfile


router = APIRouter()


@router.get(
    "/profile/me",
    response_model=ProfileResponse,
)
def get_profile(
    current_user: User = Depends(
        get_current_user
    ),
):
    return current_user


@router.put(
    "/profile",
    response_model=ProfileResponse,
)
def update_profile(
    profile: UpdateProfile,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    if profile.username:
        existing = (
            db.query(User)
            .filter(
                User.username == profile.username,
                User.id != current_user.id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken.",
            )

    for field in (
        "full_name",
        "username",
        "bio",
        "avatar",
        "preferred_language",
        "preferred_currency",
    ):
        value = getattr(profile, field)

        if value is not None:
            setattr(
                current_user,
                field,
                value,
            )

    db.commit()
    db.refresh(current_user)

    return current_user
