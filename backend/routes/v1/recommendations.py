from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user

from models.trade import Trade
from models.user import User

from services.recommendations.engine import (
    generate_recommendations,
)

router = APIRouter(
    prefix="/recommendations",
    tags=["AI Recommendations"]
)


@router.get("/")
def recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    trades = (
        db.query(Trade)
        .filter(
            Trade.user_id == current_user.id
        )
        .all()
    )

    # -------------------------------------------------
    # Placeholder data
    # These will be replaced by the real engines.
    # -------------------------------------------------

    risk = {}

    behavior = {}

    psychology = {}

    consistency = {

        "score": {
            "overall_score": 80
        },

        "trend": "Stable",

        "sessions": {},

        "weekdays": {},

        "symbols": {},

        "strategies": {}

    }

    strategies = {}

    performance = {

        "trend": "Stable",

        "monthly_growth": 0,

        "win_rate": 0,

        "profit_factor": 0,

        "consistency_score": 80

    }

    recommendations = generate_recommendations(

        risk,

        behavior,

        psychology,

        consistency,

        strategies,

        performance,

    )

    return {

        "total_trades": len(trades),

        "recommendation_count": len(
            recommendations
        ),

        "recommendations": recommendations

    }