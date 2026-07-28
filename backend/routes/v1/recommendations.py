from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.subscription import (
    require_paid_plan,
)

from models.trade import Trade
from models.user import User

from services.recommendations.engine import (
    generate_recommendations,
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
    trades = (
        db.query(Trade)
        .filter(
            Trade.user_id == current_user.id
        )
        .all()
    )

    risk = {}
    behavior = {}
    psychology = {}

    consistency = {
        "score": {
            "overall_score": 80,
        },
        "trend": "Stable",
        "sessions": {},
        "weekdays": {},
        "symbols": {},
        "strategies": {},
    }

    strategies = {}

    performance = {
        "trend": "Stable",
        "monthly_growth": 0,
        "win_rate": 0,
        "profit_factor": 0,
        "consistency_score": 80,
    }

    generated = generate_recommendations(
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
            generated
        ),
        "recommendations": generated,
    }
