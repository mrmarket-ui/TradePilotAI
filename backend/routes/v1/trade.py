from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user

from models.trade import Trade
from models.user import User

from schemas.trade import (
    TradeCreate,
    TradeUpdate,
    TradeResponse,
    TradeListResponse,
)

router = APIRouter(
    prefix="/trades",
    tags=["Trades"],
)


def get_trade(
    db: Session,
    user_id: int,
    trade_id: int,
):
    trade = (
        db.query(Trade)
        .filter(
            Trade.id == trade_id,
            Trade.user_id == user_id,
        )
        .first()
    )

    if trade is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found.",
        )

    return trade


@router.get(
    "",
    response_model=TradeListResponse,
)
def list_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    query = (
        db.query(Trade)
        .filter(
            Trade.user_id == current_user.id
        )
    )

    total = query.count()

    trades = (
        query.order_by(
            Trade.created_at.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "trades": trades,
    }


@router.post(
    "",
    response_model=TradeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_trade(
    payload: TradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    data = payload.model_dump()

    data["pair"] = data["pair"].upper().strip()
    data["direction"] = data["direction"].upper().strip()

    if data["direction"] not in ("BUY", "SELL"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Direction must be BUY or SELL.",
        )

    trade = Trade(
        user_id=current_user.id,
        **data,
    )

    db.add(trade)

    try:
        db.commit()
        db.refresh(trade)

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Trade ticket already exists.",
        )

    return trade


@router.get(
    "/{trade_id}",
    response_model=TradeResponse,
)
def get_trade_by_id(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return get_trade(
        db,
        current_user.id,
        trade_id,
    )


@router.patch(
    "/{trade_id}",
    response_model=TradeResponse,
)
def update_trade(
    trade_id: int,
    payload: TradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    trade = get_trade(
        db,
        current_user.id,
        trade_id,
    )

    updates = payload.model_dump(
        exclude_unset=True,
    )

    if "pair" in updates:
        updates["pair"] = updates["pair"].upper().strip()

    if "direction" in updates:

        direction = updates["direction"].upper().strip()

        if direction not in ("BUY", "SELL"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Direction must be BUY or SELL.",
            )

        updates["direction"] = direction

    for field, value in updates.items():
        setattr(
            trade,
            field,
            value,
        )

    try:

        db.commit()
        db.refresh(trade)

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Trade ticket already exists.",
        )

    return trade


@router.delete(
    "/{trade_id}",
)
def delete_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    trade = get_trade(
        db,
        current_user.id,
        trade_id,
    )

    db.delete(trade)
    db.commit()

    return {
        "success": True,
        "message": "Trade deleted successfully.",
    }