from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.subscription import (
    require_paid_plan,
)

from models.trade import Trade
from models.user import User

from schemas.trade_review.review import (
    TradeReviewResponse,
)

from services.trade_review.engine import (
    review_trade,
)


router = APIRouter(
    prefix="/trades",
    tags=["AI Trade Review"],
)


@router.get(
    "/{trade_id}/review",
    response_model=TradeReviewResponse,
)
def get_trade_review(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_paid_plan,
    ),
):
    trade = (
        db.query(Trade)
        .filter(
            Trade.id == trade_id,
            Trade.user_id == current_user.id,
        )
        .first()
    )

    if trade is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Trade not found.",
        )

    return review_trade(trade)
