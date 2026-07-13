from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.user import User

from schemas.weekly_review.review import (
    WeeklyReviewResponse,
)
from services.weekly_review.engine import (
    generate_weekly_review,
)


router = APIRouter(
    prefix="/reports",
    tags=["AI Reports"],
)


@router.get(
    "/weekly",
    response_model=WeeklyReviewResponse,
)
def weekly_review(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return generate_weekly_review(
        db=db,
        user_id=current_user.id,
    )
