from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.user import User

from services.dashboard.dashboard import get_dashboard

router = APIRouter(
    prefix="/analytics",
    tags=["Dashboard"]
)


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_dashboard(
        db=db,
        user_id=current_user.id
    )
