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

    if trade.profit_loss > 0:
        trade.result = "WIN"

    elif trade.profit_loss < 0:
        trade.result = "LOSS"

    else:
        trade.result = "BREAKEVEN"


    risk_distance = None

    if trade.stop_loss is not None:
        risk_distance = abs(
            trade.entry_price
            - trade.stop_loss
        )


    if (
        risk_distance is not None
        and risk_distance > 0
    ):
        trade.r_multiple = round(
            trade.profit_loss
            / risk_distance,
            3,
        )

    else:
        trade.r_multiple = None


    trade.status = "closed"

    trade.closed_at = (
        datetime.utcnow()
    )


    if trade.opened_at:
        duration = (
            trade.closed_at
            - trade.opened_at
        )

        trade.duration_minutes = max(
            0,
            int(
                duration.total_seconds()
                // 60
            ),
        )

    db.commit()
    db.refresh(trade)

    return trade
@router.get("/paper-trades/analytics")
def get_paper_trade_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    rows = (
        db.query(
            PaperTrade,
            AISignal,
            StrategyProfile,
        )
        .join(
            AISignal,
            PaperTrade.signal_id
            == AISignal.id,
        )
        .outerjoin(
            StrategyProfile,
            AISignal.strategy_id
            == StrategyProfile.id,
        )
        .filter(
            PaperTrade.user_id
            == current_user.id,
            PaperTrade.status
            == "closed",
        )
        .order_by(
            PaperTrade.closed_at.desc()
        )
        .all()
    )

    closed_trades = len(rows)

    wins = sum(
        1
        for trade, _, _ in rows
        if trade.result == "WIN"
    )

    losses = sum(
        1
        for trade, _, _ in rows
        if trade.result == "LOSS"
    )

    breakeven = sum(
        1
        for trade, _, _ in rows
        if trade.result == "BREAKEVEN"
    )

    win_rate = (
        round(
            wins / closed_trades * 100,
            2,
        )
        if closed_trades
        else 0.0
    )

    r_values = [
        trade.r_multiple
        for trade, _, _ in rows
        if trade.r_multiple is not None
    ]

    total_r = round(
        sum(r_values),
        3,
    )

    average_r = (
        round(
            total_r / len(r_values),
            3,
        )
        if r_values
        else 0.0
    )

    durations = [
        trade.duration_minutes
        for trade, _, _ in rows
        if trade.duration_minutes
        is not None
    ]

    average_duration_minutes = (
        round(
            sum(durations)
            / len(durations),
            1,
        )
        if durations
        else 0.0
    )

    strategy_groups = {}

    symbol_groups = {}

    timeframe_groups = {}

    confidence_groups = {
        "60-69": [],
        "70-79": [],
        "80-89": [],
        "90-100": [],
    }

    for trade, signal, strategy in rows:

        strategy_name = (
            strategy.name
            if strategy
            else "Unknown Strategy"
        )

        strategy_id = (
            strategy.id
            if strategy
            else None
        )

        strategy_key = (
            strategy_id,
            strategy_name,
        )

        strategy_groups.setdefault(
            strategy_key,
            [],
        ).append(trade)

        symbol_groups.setdefault(
            trade.symbol,
            [],
        ).append(trade)

        timeframe = (
            signal.timeframe
            or "Unknown"
        )

        timeframe_groups.setdefault(
            timeframe,
            [],
        ).append(trade)

        confidence = (
            signal.confidence
            or 0
        )

        if 60 <= confidence < 70:
            confidence_groups[
                "60-69"
            ].append(trade)

        elif 70 <= confidence < 80:
            confidence_groups[
                "70-79"
            ].append(trade)

        elif 80 <= confidence < 90:
            confidence_groups[
                "80-89"
            ].append(trade)

        elif confidence >= 90:
            confidence_groups[
                "90-100"
            ].append(trade)


    def calculate_group_metrics(
        grouped_trades,
    ):
        total = len(
            grouped_trades
        )

        group_wins = sum(
            1
            for trade
            in grouped_trades
            if trade.result == "WIN"
        )

        group_losses = sum(
            1
            for trade
            in grouped_trades
            if trade.result == "LOSS"
        )

        group_breakeven = sum(
            1
            for trade
            in grouped_trades
            if trade.result
            == "BREAKEVEN"
        )

        group_r_values = [
            trade.r_multiple
            for trade
            in grouped_trades
            if trade.r_multiple
            is not None
        ]

        group_total_r = round(
            sum(group_r_values),
            3,
        )

        return {
            "trades": total,

            "wins":
                group_wins,

            "losses":
                group_losses,

            "breakeven":
                group_breakeven,

            "win_rate": (
                round(
                    group_wins
                    / total
                    * 100,
                    2,
                )
                if total
                else 0.0
            ),

            "total_r":
                group_total_r,

            "average_r": (
                round(
                    group_total_r
                    / len(
                        group_r_values
                    ),
                    3,
                )
                if group_r_values
                else 0.0
            ),
        }


    strategies = []

    for (
        strategy_id,
        strategy_name,
    ), grouped_trades in (
        strategy_groups.items()
    ):
        strategies.append({
            "strategy_id":
                strategy_id,

            "strategy_name":
                strategy_name,

            **calculate_group_metrics(
                grouped_trades
            ),
        })


    strategies.sort(
        key=lambda item: (
            item["total_r"],
            item["win_rate"],
        ),
        reverse=True,
    )


    symbols = [
        {
            "symbol": symbol,
            **calculate_group_metrics(
                grouped_trades
            ),
        }
        for symbol, grouped_trades
        in symbol_groups.items()
    ]

    symbols.sort(
        key=lambda item:
            item["total_r"],
        reverse=True,
    )


    timeframes = [
        {
            "timeframe": timeframe,
            **calculate_group_metrics(
                grouped_trades
            ),
        }
        for timeframe, grouped_trades
        in timeframe_groups.items()
    ]

    timeframes.sort(
        key=lambda item:
            item["total_r"],
        reverse=True,
    )


    confidence_bands = [
        {
            "band": band,
            **calculate_group_metrics(
                grouped_trades
            ),
        }
        for band, grouped_trades
        in confidence_groups.items()
        if grouped_trades
    ]


    return {
        "summary": {
            "closed_trades":
                closed_trades,

            "wins":
                wins,

            "losses":
                losses,

            "breakeven":
                breakeven,

            "win_rate":
                win_rate,

            "total_r":
                total_r,

            "average_r":
                average_r,

            "average_duration_minutes":
                average_duration_minutes,
        },

        "strategies":
            strategies,

        "symbols":
            symbols,

        "timeframes":
            timeframes,

        "confidence_bands":
            confidence_bands,
    }
