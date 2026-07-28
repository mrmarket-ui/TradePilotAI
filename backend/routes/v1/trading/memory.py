from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.subscription import (
    require_paid_plan,
)

from models.trade import Trade
from models.user import User

from services.ai_engine.market_memory import (
    MarketMemory,
)


router = APIRouter()


@router.get("/memory")
def trade_memory(
    current_user: User = Depends(
        require_paid_plan,
    ),
    db: Session = Depends(get_db),
):
    trades = (
        db.query(Trade)
        .filter(
            Trade.user_id
            == current_user.id
        )
        .all()
    )

    return MarketMemory.summarize(
        trades,
    )
