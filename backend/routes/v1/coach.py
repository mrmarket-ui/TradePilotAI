from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user

from models.user import User

from services.coach.engine import build_ai_dashboard

router = APIRouter(
    prefix="/coach",
    tags=["AI Coach"]
)

@router.get("/")
def ai_coach(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return build_ai_dashboard(
        db=db,
        user_id=current_user.id
    )