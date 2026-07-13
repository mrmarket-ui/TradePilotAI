from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user

from models.user import User
from models.trade import Trade

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
    current_user: User = Depends(get_current_user),
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
            status_code=404,
            detail="Trade not found.",
        )

    return review_trade(trade)
