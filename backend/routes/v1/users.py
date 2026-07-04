from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.user import User

router = APIRouter()


@router.get("/users/profile")
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }