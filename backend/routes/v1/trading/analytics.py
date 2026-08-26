from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from database.database import (
    get_db,
)

from dependencies.auth import (
    get_current_user,
)

from models.user import User

from services.analysis.loader import (
    load_user_trades,
)

from services.analytics.engine import (
    calculate_statistics,
)

from services.analytics.calendar import (
    build_trading_calendar,
)


router = APIRouter(
    prefix="/trading",
    tags=["Advanced Analytics"],
)


@router.get("/analytics")
def analytics(
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    return calculate_statistics(
        db=db,
        user_id=current_user.id,
    )


@router.get("/calendar")
def trading_calendar(
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    trades = load_user_trades(
        db=db,
        user_id=current_user.id,
    )

    days = build_trading_calendar(
        trades
    )

    return {
        "total_days":
            len(days),

        "days":
            days,
    }
