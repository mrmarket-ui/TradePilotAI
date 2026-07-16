from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.user import User

from services.analytics.engine import calculate_statistics

router = APIRouter(
    prefix="/trading",
    tags=["Analytics"]
)


@router.get("/analytics")
def analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return calculate_statistics(
        db=db,
        user_id=current_user.id
    )
