from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user

from models.user import User

from schemas.profile_schema import ProfileResponse
from schemas.update_profile import UpdateProfile

router = APIRouter()


@router.get("/profile/me", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.put("/profile")
def update_profile(
    profile: UpdateProfile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if profile.username:

        existing = db.query(User).filter(
            User.username == profile.username,
            User.id != current_user.id
        ).first()

        if existing:
            return {"error": "Username already taken"}

    if profile.full_name is not None:
        current_user.full_name = profile.full_name

    if profile.username is not None:
        current_user.username = profile.username

    if profile.bio is not None:
        current_user.bio = profile.bio

    if profile.avatar is not None:
        current_user.avatar = profile.avatar

    db.commit()
    db.refresh(current_user)

    return current_user