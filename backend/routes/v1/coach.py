from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.subscription import require_paid_plan
from models.user import User

from services.analysis.service import AnalysisService
from services.coach.engine import build_ai_coach


router = APIRouter(
    prefix="/coach",
    tags=["AI Coach"],
)


@router.get("/")
def get_ai_coach(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_paid_plan,
    ),
):
    analysis = AnalysisService.analyze(
        db=db,
        user_id=current_user.id,
    )

    analysis_data = analysis.model_dump()

    coach = build_ai_coach(
        analysis_data,
    )

    return {
        "coach": coach,
        "analysis": analysis_data,
    }
