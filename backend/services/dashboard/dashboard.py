"""
TradePilot AI unified dashboard service.

Builds the live dashboard from:
- Trading statistics
- Equity progression
- Monthly performance
- Symbol activity
- Recent trades
- Trader DNA
- Psychology and consistency
- Active Strategy Brain profile
- AI dashboard intelligence
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from models.strategy_profile import StrategyProfile

from services.analysis.loader import load_user_trades
from services.analysis.service import AnalysisService
from services.analytics.engine import (
    calculate_statistics_from_trades,
)
from services.dashboard.intelligence.engine import (
    generate_dashboard_intelligence,
)


def _serialize_datetime(
    value: datetime | None,
) -> str | None:
    if value is None:
        return None

    return value.isoformat()


def _serialize_trade(
    trade: Any,
) -> dict[str, Any]:
    return {
        "id": trade.id,
        "pair": trade.pair,
        "direction": trade.direction,
        "profit": round(
            float(trade.profit or 0),
            2,
        ),
        "lot_size": trade.lot_size,
        "strategy": trade.strategy,
        "opened_at": _serialize_datetime(
            trade.opened_at
        ),
        "closed_at": _serialize_datetime(
            trade.closed_at
        ),
    }


def _build_equity_curve(
    trades: list[Any],
) -> list[dict[str, Any]]:
    closed_trades = sorted(
        [
            trade
            for trade in trades
            if trade.closed_at is not None
        ],
        key=lambda trade: trade.closed_at,
    )

    equity_curve: list[dict[str, Any]] = []
    balance = 0.0

    for trade in closed_trades:
        balance += float(
            trade.profit or 0
        )

        equity_curve.append({
            "date": _serialize_datetime(
                trade.closed_at
            ),
            "balance": round(
                balance,
                2,
            ),
        })

    return equity_curve


def _build_monthly_profit(
    trades: list[Any],
) -> dict[str, float]:
    monthly_profit: dict[str, float] = {}

    for trade in trades:
        if trade.closed_at is None:
            continue

        month = trade.closed_at.strftime(
            "%Y-%m"
        )

        monthly_profit[month] = (
            monthly_profit.get(
                month,
                0.0,
            )
            + float(trade.profit or 0)
        )

    return {
        month: round(
            profit,
            2,
        )
        for month, profit in sorted(
            monthly_profit.items()
        )
    }


def _build_symbol_activity(
    trades: list[Any],
) -> list[dict[str, Any]]:
    counter = Counter(
        trade.pair
        for trade in trades
        if trade.pair
    )

    return [
        {
            "pair": pair,
            "count": count,
        }
        for pair, count
        in counter.most_common()
    ]


def _today_profit(
    trades: list[Any],
) -> float:
    today = datetime.now(
        timezone.utc
    ).date()

    profit = 0.0

    for trade in trades:
        closed_at = trade.closed_at

        if closed_at is None:
            continue

        trade_date = closed_at.date()

        if trade_date == today:
            profit += float(
                trade.profit or 0
            )

    return round(
        profit,
        2,
    )


def _today_trade_count(
    trades: list[Any],
) -> int:
    today = datetime.now(
        timezone.utc
    ).date()

    count = 0

    for trade in trades:
        activity_time = (
            trade.opened_at
            or trade.created_at
        )

        if (
            activity_time is not None
            and activity_time.date() == today
        ):
            count += 1

    return count


def _active_strategy(
    db: Session,
    user_id: int,
) -> dict[str, Any] | None:
    strategy = (
        db.query(StrategyProfile)
        .filter(
            StrategyProfile.user_id
            == user_id,
            StrategyProfile.is_active
            .is_(True),
        )
        .order_by(
            StrategyProfile.updated_at.desc()
        )
        .first()
    )

    if strategy is None:
        return None

    return {
        "id": strategy.id,
        "name": strategy.name,
        "description":
            strategy.description,
        "markets":
            strategy.markets or [],
        "sessions":
            strategy.sessions or [],
        "timeframes":
            strategy.timeframes or [],
        "entry_rules":
            strategy.entry_rules or [],
        "confirmations":
            strategy.confirmations or [],
        "max_risk_percent":
            strategy.max_risk_percent,
        "max_trades_per_day":
            strategy.max_trades_per_day,
        "requires_user_approval":
            strategy.requires_user_approval,
        "updated_at":
            _serialize_datetime(
                strategy.updated_at
            ),
    }


def _extract_consistency_score(
    analysis: Any,
) -> float:
    consistency = analysis.consistency

    score = getattr(
        consistency,
        "score",
        {},
    )

    if isinstance(score, dict):
        return round(
            float(
                score.get(
                    "overall_score",
                    0,
                )
                or 0
            ),
            2,
        )

    return round(
        float(score or 0),
        2,
    )


def _extract_trader_dna(
    analysis: Any,
) -> dict[str, Any]:
    trader_dna = analysis.trader_dna

    if hasattr(
        trader_dna,
        "model_dump",
    ):
        return trader_dna.model_dump()

    if isinstance(
        trader_dna,
        dict,
    ):
        return trader_dna

    return {}


def _extract_psychology(
    analysis: Any,
) -> dict[str, Any]:
    psychology = analysis.psychology

    if hasattr(
        psychology,
        "model_dump",
    ):
        return psychology.model_dump()

    if isinstance(
        psychology,
        dict,
    ):
        return psychology

    return {}


def _extract_recommendations(
    analysis: Any,
) -> list[dict[str, Any]]:
    recommendations = []

    for item in analysis.recommendations[:5]:
        if hasattr(
            item,
            "model_dump",
        ):
            recommendations.append(
                item.model_dump()
            )

        elif isinstance(
            item,
            dict,
        ):
            recommendations.append(
                item
            )

    return recommendations


def get_dashboard(
    db: Session,
    user_id: int,
) -> dict[str, Any]:
    trades = load_user_trades(
        db=db,
        user_id=user_id,
    )

    statistics = (
        calculate_statistics_from_trades(
            trades
        )
    )

    analysis = AnalysisService.analyze(
        db=db,
        user_id=user_id,
    )

    intelligence = (
        generate_dashboard_intelligence(
            analysis
        )
    )

    active_strategy = _active_strategy(
        db=db,
        user_id=user_id,
    )

    recent_trades = sorted(
        trades,
        key=lambda trade: (
            trade.closed_at
            or trade.opened_at
            or trade.created_at
        ),
        reverse=True,
    )[:10]

    trader_dna = _extract_trader_dna(
        analysis
    )

    psychology = _extract_psychology(
        analysis
    )

    return {
        "intelligence": intelligence,

        "summary": statistics,

        "overview": {
            "today_profit":
                _today_profit(trades),

            "today_trades":
                _today_trade_count(
                    trades
                ),

            "current_strategy":
                active_strategy,

            "consistency_score":
                _extract_consistency_score(
                    analysis
                ),

            "discipline_score":
                float(
                    psychology.get(
                        "discipline_score",
                        0,
                    )
                    or 0
                ),

            "confidence_score":
                float(
                    psychology.get(
                        "confidence_score",
                        0,
                    )
                    or 0
                ),

            "risk_limit_percent":
                (
                    active_strategy[
                        "max_risk_percent"
                    ]
                    if active_strategy
                    else None
                ),

            "approval_required":
                (
                    active_strategy[
                        "requires_user_approval"
                    ]
                    if active_strategy
                    else True
                ),
        },

        "active_strategy":
            active_strategy,

        "equity_curve":
            _build_equity_curve(
                trades
            ),

        "monthly_profit":
            _build_monthly_profit(
                trades
            ),

        "symbols":
            _build_symbol_activity(
                trades
            ),

        "recent_trades": [
            _serialize_trade(
                trade
            )
            for trade in recent_trades
        ],

        "trader_dna":
            trader_dna,

        "psychology":
            psychology,

        "recommendations":
            _extract_recommendations(
                analysis
            ),

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }
