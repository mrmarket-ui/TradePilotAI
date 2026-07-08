from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from models.trade import Trade

router = APIRouter(
    prefix="/trades",
    tags=["Trades"]
)


@router.get("/")
def get_trades(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    trades = (
        db.query(Trade)
        .filter(Trade.user_id == current_user.id)
        .order_by(Trade.closed_at.desc())
        .all()
    )

    return trades
