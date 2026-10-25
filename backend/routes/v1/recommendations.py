from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.subscription import (
    require_paid_plan,
)

from models.user import User

from services.analysis.pipeline import (
    run_analysis_pipeline,
)
from services.analysis.sufficiency import (
    MIN_TRADES_TRADER_DNA,
)


router = APIRouter(
    prefix="/recommendations",
    tags=["AI Recommendations"],
)


@router.get("/")
def recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_paid_plan,
    ),
):
    """
    Recommendations built from the user's real analysis.

    This endpoint used to pass hard-coded placeholder values into the
    recommendation engine, so every trader received the same advice.
    """

    result = run_analysis_pipeline(
        db=db,
        user_id=current_user.id,
    )

    total_trades = len(result["trades"])

    if total_trades < MIN_TRADES_TRADER_DNA:
        return {
            "total_trades": total_trades,
            "recommendation_count": 0,
            "recommendations": [],
            "sufficient_data": False,
            "trades_needed": MIN_TRADES_TRADER_DNA - total_trades,
        }

    generated = result["recommendations"]

    return {
        "total_trades": total_trades,
        "recommendation_count": len(generated),
        "recommendations": generated,
        "sufficient_data": True,
        "trades_needed": 0,
    }