from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from services.analysis.loader import load_user_trades
from services.analysis.service import AnalysisService
from services.analytics.engine import (
    calculate_statistics_from_trades,
)


def _to_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    return {}


def _month_start(now: datetime) -> datetime:
    return now.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


def _score_month(
    metrics: dict,
    analysis: dict,
) -> float:
    score = 50.0

    if metrics["net_profit"] > 0:
        score += 15
    else:
        score -= 15

    if metrics["win_rate"] >= 50:
        score += 10
    elif metrics["win_rate"] < 30:
        score -= 10

    if metrics["profit_factor"] >= 1.5:
        score += 15
    elif metrics["profit_factor"] < 1:
        score -= 15

    behavior = analysis.get("behavior", {})

    if behavior.get("revenge_trading"):
        score -= 10

    if behavior.get("fomo_detected"):
        score -= 5

    return round(
        max(0.0, min(100.0, score)),
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


def _summary(
    metrics: dict,
    analysis: dict,
) -> str:
    total = metrics["total_trades"]

    if total == 0:
        return (
            "No completed trades were recorded during this month."
        )

    if metrics["net_profit"] > 0:
        opening = (
            "You completed a profitable month."
        )
    else:
        opening = (
            "You completed the month at a loss."
        )

    message = (
        f"{opening} You recorded {total} trades, "
        f"a {metrics['win_rate']}% win rate and a "
        f"profit factor of {metrics['profit_factor']}."
    )

    behavior = analysis.get("behavior", {})

    if behavior.get("revenge_trading"):
        message += (
            " Revenge trading remains your highest-priority "
            "behavioral issue."
        )

    elif behavior.get("fomo_detected"):
        message += (
            " FOMO entries continue to reduce setup quality."
        )

    return message


def _mission(analysis: dict) -> str:
    behavior = analysis.get("behavior", {})
    performance = analysis.get("performance", {})
    risk = analysis.get("risk", {})

    if behavior.get("revenge_trading"):
        return (
            "Complete next month with zero revenge trades and "
            "take a mandatory break after every losing trade."
        )

    if behavior.get("fomo_detected"):
        return (
            "Take only entries that satisfy your full confirmation "
            "checklist."
        )

    if risk.get("expectancy", 0) < 0:
        return (
            "Achieve positive expectancy by reducing low-quality "
            "trades and protecting capital."
        )

    if performance.get("profit_factor", 0) < 1:
        return (
            "Raise your profit factor above 1 by improving setup "
            "quality and reward-to-risk."
        )

    return (
        "Repeat your best process without increasing risk."
    )


def generate_monthly_review(
    db,
    user_id: int,
) -> dict:
    now = datetime.now(timezone.utc)
    start = _month_start(now)

    trades = load_user_trades(
        db=db,
        user_id=user_id,
    )

    monthly_trades = []

    for trade in trades:
        closed_at = getattr(
            trade,
            "closed_at",
            None,
        )

        if closed_at is None:
            continue

        if closed_at.tzinfo is None:
            comparison_start = start.replace(
                tzinfo=None
            )
        else:
            comparison_start = start

        if closed_at >= comparison_start:
            monthly_trades.append(trade)

    metrics = calculate_statistics_from_trades(
        monthly_trades
    )

    analysis_model = AnalysisService.analyze(
        db=db,
        user_id=user_id,
    )

    analysis = _to_dict(
        analysis_model
    )

    trader_dna = analysis.get(
        "trader_dna",
        {},
    )

    score = _score_month(
        metrics=metrics,
        analysis=analysis,
    )

    return {
        "period_start": start.date().isoformat(),
        "period_end": now.date().isoformat(),
        "grade": _grade(score),
        "score": score,
        "summary": _summary(
            metrics=metrics,
            analysis=analysis,
        ),
        "metrics": metrics,
        "trader_profile": trader_dna.get(
            "profile",
            "Developing Trader",
        ),
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
        "next_month_mission": _mission(
            analysis
        ),
    }
