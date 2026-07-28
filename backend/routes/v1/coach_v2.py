from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.subscription import require_paid_plan
from models.user import User

from services.analysis.service import AnalysisService
from services.coach.v2.engine import generate_ai_coach


router = APIRouter(
    prefix="/coach",
    tags=["AI Coach"],
)


@router.get("")
def coach(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_paid_plan,
    ),
):
    analysis = AnalysisService.analyze(
        db=db,
        user_id=current_user.id,
    )

    return generate_ai_coach(
        analysis,
    )
