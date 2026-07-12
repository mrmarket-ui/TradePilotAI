"""
TradePilot AI Chat Context Builder.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from services.analysis.service import AnalysisService
from services.analysis.loader import load_user_trades


def _to_dict(value: Any) -> dict:
    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    return {}


def _serialize_trade(trade: Any) -> dict:
    return {
        "pair": getattr(trade, "pair", None),
        "direction": getattr(trade, "direction", None),
        "profit": float(
            getattr(trade, "profit", 0) or 0
        ),
        "strategy": getattr(
            trade,
            "strategy",
            None,
        ),
        "opened_at": getattr(
            trade,
            "opened_at",
            None,
        ),
        "closed_at": getattr(
            trade,
            "closed_at",
            None,
        ),
    }


def build_chat_context(
    db: Session,
    user_id: int,
) -> dict:
    analysis = AnalysisService.analyze(
        db=db,
        user_id=user_id,
    )

    trades = load_user_trades(
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
    )[:20]

    data = _to_dict(analysis)

    return {
        "risk": _to_dict(
            data.get("risk")
        ),
        "behavior": _to_dict(
            data.get("behavior")
        ),
        "psychology": _to_dict(
            data.get("psychology")
        ),
        "performance": _to_dict(
            data.get("performance")
        ),
        "consistency": _to_dict(
            data.get("consistency")
        ),
        "trader_dna": _to_dict(
            data.get("trader_dna")
        ),
        "recommendations": [
            _to_dict(item)
            for item in data.get(
                "recommendations",
                [],
            )
        ],
        "recent_trades": [
            _serialize_trade(trade)
            for trade in recent_trades
        ],
        "trade_count": len(trades),
    }
