from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.user import User

from schemas.monthly_review.review import (
    MonthlyReviewResponse,
)
from services.monthly_review.engine import (
    generate_monthly_review,
)


router = APIRouter(
    prefix="/reports",
    tags=["AI Reports"],
)


@router.get(
    "/monthly",
    response_model=MonthlyReviewResponse,
)
def monthly_review(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return generate_monthly_review(
        db=db,
        user_id=current_user.id,
    )
