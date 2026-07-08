from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from database.database import get_db

from dependencies.auth import get_current_user

from models.user import User

from services.analytics.charts import (
    get_equity_curve,
    get_monthly_profit,
    get_pair_performance,
    get_win_loss
)

router = APIRouter(
    prefix="/analytics/charts",
    tags=["Analytics Charts"]
)


@router.get("/equity")
def equity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_equity_curve(
        db,
        current_user.id
    )


@router.get("/monthly-profit")
def monthly_profit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_monthly_profit(
        db,
        current_user.id
    )


@router.get("/pairs")
def pairs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_pair_performance(
        db,
        current_user.id
    )


@router.get("/win-loss")
def win_loss(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_win_loss(
        db,
        current_user.id
    )