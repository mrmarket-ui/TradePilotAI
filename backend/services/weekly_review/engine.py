from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from services.analysis.service import AnalysisService
from services.analysis.loader import load_user_trades
from services.weekly_review.metrics import (
    calculate_weekly_metrics,
)
from services.weekly_review.summary import (
    generate_weekly_summary,
)
from services.weekly_review.mission import (
    generate_weekly_mission,
)


def _to_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    return {}


def _score_week(metrics: dict) -> float:
    score = 50.0

    if metrics["net_profit"] > 0:
        score += 15

    if metrics["win_rate"] >= 50:
        score += 15

    if metrics["profit_factor"] >= 1.5:
        score += 15

    if metrics["profit_factor"] < 1:
        score -= 15

    if metrics["net_profit"] < 0:
        score -= 15

    return round(
        max(0, min(100, score)),
        1,
    )


def _grade(score: float) -> str:
    if score >= 90:
        return "A"

    if score >= 80:
        return "B"

    if score >= 70:
        return "C"

    if score >= 60:
        return "D"

    return "F"


def generate_weekly_review(
    db,
    user_id: int,
) -> dict:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)

    all_trades = load_user_trades(
        db=db,
        user_id=user_id,
    )

    weekly_trades = [
        trade
        for trade in all_trades
        if (
            getattr(trade, "closed_at", None)
            and getattr(trade, "closed_at") >= start.replace(
                tzinfo=getattr(
                    getattr(trade, "closed_at"),
                    "tzinfo",
                    None,
                )
            )
        )
    ]

    analysis_model = AnalysisService.analyze(
        db=db,
        user_id=user_id,
    )

    analysis = _to_dict(analysis_model)

    metrics = calculate_weekly_metrics(
        weekly_trades
    )

    score = _score_week(metrics)

    trader_dna = analysis.get(
        "trader_dna",
        {},
    )

    return {
        "period_start": start.date().isoformat(),
        "period_end": now.date().isoformat(),
        "grade": _grade(score),
        "score": score,
        "summary": generate_weekly_summary(
            metrics=metrics,
            behavior=analysis.get(
                "behavior",
                {},
            ),
        ),
        "metrics": metrics,
        "strengths": trader_dna.get(
            "strengths",
            [],
        )[:3],
        "weaknesses": trader_dna.get(
            "weaknesses",
            [],
        )[:3],
        "recommendations": analysis.get(
            "recommendations",
            [],
        )[:5],
        "next_week_mission": generate_weekly_mission(
            analysis
        ),
    }
