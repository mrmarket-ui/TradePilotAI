from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.subscription import (
    require_premium_plan,
)
from models.ai_signal import (
    AISignal,
    PaperTrade,
)
from models.strategy_profile import (
    StrategyProfile,
)
from models.user import User
from schemas.ai_signal import (
    PaperTradeClose,
    PaperTradeCreate,
    SignalApproval,
)
from services.ai_engine.strategy_signal import (
    analyze_chart,
)


router = APIRouter(
    prefix="/ai-signals",
    tags=["AI Signals"],
)


UPLOAD_DIR = Path(
    "storage/signal_charts"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def get_owned_signal(
    db: Session,
    user_id: int,
    signal_id: int,
):
    signal = (
        db.query(AISignal)
        .filter(
            AISignal.id == signal_id,
            AISignal.user_id
            == user_id,
        )
        .first()
    )

    if signal is None:
        raise HTTPException(
            status_code=404,
            detail="Signal not found.",
        )

    return signal


@router.post("/analyze-chart")
async def create_chart_signal(
    symbol: str = Form(...),
    timeframe: str = Form(...),
    strategy_id: int = Form(...),
    chart: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    strategy = (
        db.query(StrategyProfile)
        .filter(
            StrategyProfile.id
            == strategy_id,
            StrategyProfile.user_id
            == current_user.id,
            StrategyProfile.is_archived
            .is_(False),
        )
        .first()
    )

    if strategy is None:
        raise HTTPException(
            status_code=404,
            detail="Strategy not found.",
        )

    content_type = (
        chart.content_type
        or ""
    ).lower()

    if not content_type.startswith(
        "image/"
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Chart must be an image."
            ),
        )

    contents = await chart.read()

    if len(contents) > (
        15 * 1024 * 1024
    ):
        raise HTTPException(
            status_code=413,
            detail=(
                "Chart image exceeds 15 MB."
            ),
        )

    extension = (
        Path(
            chart.filename
            or "chart.png"
        )
        .suffix
        .lower()
        or ".png"
    )

    user_dir = (
        UPLOAD_DIR /
        str(current_user.id)
    )

    user_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        user_dir /
        f"{uuid4().hex}{extension}"
    )

    path.write_bytes(
        contents
    )

    result = analyze_chart(
        image_path=str(path),
        strategy=strategy,
        symbol=symbol.strip().upper(),
        timeframe=timeframe.strip(),
    )

    direction = result[
        "direction"
    ]

    if (
        result["confidence"] < 60
        or result["setup_score"] < 60
    ):
        direction = "NO_TRADE"

    signal = AISignal(
        user_id=current_user.id,
        strategy_id=strategy.id,
        symbol=symbol.strip().upper(),
        timeframe=timeframe.strip(),
        direction=direction,
        confidence=result[
            "confidence"
        ],
        setup_score=result[
            "setup_score"
        ],
        entry_low=result.get(
            "entry_low"
        ),
        entry_high=result.get(
            "entry_high"
        ),
        stop_loss=result.get(
            "stop_loss"
        ),
        take_profit_1=result.get(
            "take_profit_1"
        ),
        take_profit_2=result.get(
            "take_profit_2"
        ),
        take_profit_3=result.get(
            "take_profit_3"
        ),
        risk_reward=result.get(
            "risk_reward"
        ),
        matched_rules=result.get(
            "matched_rules",
            [],
        ),
        missing_rules=result.get(
            "missing_rules",
            [],
        ),
        reasoning=result.get(
            "reasoning"
        ),
        invalidation=result.get(
            "invalidation"
        ),
        chart_path=str(path),
    )

    db.add(signal)
    db.commit()
    db.refresh(signal)

    return signal


@router.get("")
def signal_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    signals = (
        db.query(AISignal)
        .filter(
            AISignal.user_id
            == current_user.id
        )
        .order_by(
            AISignal.created_at.desc()
        )
        .limit(100)
        .all()
    )

    return {
        "total": len(signals),
        "signals": signals,
    }


@router.patch(
    "/{signal_id}/approval"
)
def approve_signal(
    signal_id: int,
    payload: SignalApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    signal = get_owned_signal(
        db,
        current_user.id,
        signal_id,
    )

    signal.user_approved = (
        payload.approved
    )

    signal.status = (
        "approved"
        if payload.approved
        else "rejected"
    )

    db.commit()
    db.refresh(signal)

    return {
        "id": signal.id,
        "approved":
            signal.user_approved,
        "status":
            signal.status,
    }


@router.post("/paper-trades")
def create_paper_trade(
    payload: PaperTradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    signal = get_owned_signal(
        db,
        current_user.id,
        payload.signal_id,
    )

    if signal.direction == "NO_TRADE":
        raise HTTPException(
            status_code=400,
            detail=(
                "NO_TRADE signals cannot "
                "be executed."
            ),
        )

    strategy = None

    if signal.strategy_id:
        strategy = (
            db.query(
                StrategyProfile
            )
            .filter(
                StrategyProfile.id
                == signal.strategy_id
            )
            .first()
        )

    max_risk = (
        strategy.max_risk_percent
        if strategy
        else 0.5
    )

    if (
        payload.risk_percent
        > max_risk
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Risk exceeds the strategy "
                f"limit of {max_risk}%."
            ),
        )

    trade = PaperTrade(
        user_id=current_user.id,
        signal_id=signal.id,
        symbol=signal.symbol,
        direction=signal.direction,
        entry_price=
            payload.entry_price,
        stop_loss=
            signal.stop_loss,
        take_profit=
            signal.take_profit_1,
        risk_percent=
            payload.risk_percent,
    )

    db.add(trade)

    signal.status = (
        "paper_executed"
    )

    db.commit()
    db.refresh(trade)

    return trade


@router.get("/paper-trades")
def list_paper_trades(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    trades = (
        db.query(PaperTrade)
        .filter(
            PaperTrade.user_id
            == current_user.id
        )
        .order_by(
            PaperTrade.opened_at.desc()
        )
        .all()
    )

    return {
        "total": len(trades),
        "trades": trades,
    }


@router.patch(
    "/paper-trades/{trade_id}/close"
)
def close_paper_trade(
    trade_id: int,
    payload: PaperTradeClose,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    trade = (
        db.query(PaperTrade)
        .filter(
            PaperTrade.id
            == trade_id,
            PaperTrade.user_id
            == current_user.id,
        )
        .first()
    )

    if trade is None:
        raise HTTPException(
            status_code=404,
            detail="Paper trade not found.",
        )

    if trade.status != "open":
        raise HTTPException(
            status_code=400,
            detail=(
                "Paper trade is already closed."
            ),
        )

    trade.exit_price = (
        payload.exit_price
    )

    multiplier = (
        1
        if trade.direction == "BUY"
        else -1
    )

    trade.profit_loss = (
        trade.exit_price
        - trade.entry_price
    ) * multiplier

    trade.status = "closed"

    trade.closed_at = (
        datetime.utcnow()
    )

    db.commit()
    db.refresh(trade)

    return trade
