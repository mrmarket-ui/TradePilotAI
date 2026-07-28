from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from dependencies.subscription import (
    require_paid_plan,
)

from models.user import User

from services.dashboard.dashboard import (
    get_dashboard,
)
from services.analysis.service import (
    AnalysisService,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    return get_dashboard(
        db=db,
        user_id=current_user.id,
    )


@router.get("/analysis")
def analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_paid_plan,
    ),
):
    """
    Complete premium intelligence pipeline.

    Returns:
    - Performance
    - Risk
    - Behaviour
    - Psychology
    - Consistency
    - Trader DNA
    - Recommendations
    """

    return AnalysisService.analyze(
        db=db,
        user_id=current_user.id,
    )
