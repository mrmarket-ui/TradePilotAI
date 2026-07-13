"""
TradePilot AI unified intelligence pipeline.

Loads the trader's genuine market trades once and runs every
analytics and intelligence engine using the same dataset.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from services.analysis.loader import load_user_trades
from services.analytics.engine import calculate_statistics_from_trades
from services.analytics.risk import build_risk_summary
from services.behavior.engine import analyze_behavior
from services.consistency.engine import analyze_consistency
from services.psychology.engine import analyze_psychology
from services.recommendations.engine import generate_recommendations
from services.trader_dna.engine import analyze_trader_dna


def _monthly_growth(consistency: dict[str, Any]) -> float:
    monthly = consistency.get("monthly_progress", {})

    if not isinstance(monthly, dict) or len(monthly) < 2:
        return 0.0

    ordered_months = sorted(monthly.keys())

    previous_data = monthly.get(
        ordered_months[-2],
        {},
    )
    current_data = monthly.get(
        ordered_months[-1],
        {},
    )

    previous_profit = float(
        previous_data.get("profit", 0) or 0
    )
    current_profit = float(
        current_data.get("profit", 0) or 0
    )

    if previous_profit == 0:
        return 100.0 if current_profit > 0 else 0.0

    growth = (
        (current_profit - previous_profit)
        / abs(previous_profit)
    ) * 100

    return round(growth, 2)


def _consistency_score(
    consistency: dict[str, Any],
) -> float:
    score = consistency.get("score", 0)

    if isinstance(score, dict):
        return float(
            score.get("overall_score", 0) or 0
        )

    return float(score or 0)


def run_analysis_pipeline(
    db: Session,
    user_id: int,
) -> dict[str, Any]:
    """
    Run the complete TradePilot AI intelligence pipeline.

    Database access occurs once through load_user_trades().
    """

    trades = load_user_trades(
        db=db,
        user_id=user_id,
    )

    statistics = calculate_statistics_from_trades(
        trades
    )

    risk = build_risk_summary(
        trades
    )

    behavior = analyze_behavior(
        trades
    )

    psychology = analyze_psychology(
        trades=trades,
        behavior=behavior,
    )

    consistency = analyze_consistency(
        trades=trades,
        statistics=statistics,
        risk=risk,
        psychology=psychology,
        behavior=behavior,
    )

    performance = {
        "win_rate": float(
            statistics.get("win_rate", 0) or 0
        ),
        "profit_factor": float(
            statistics.get("profit_factor", 0) or 0
        ),
        "monthly_growth": _monthly_growth(
            consistency
        ),
        "consistency_score": _consistency_score(
            consistency
        ),
        "trend": consistency.get(
            "trend",
            "Stable",
        ),
    }

    trader_dna = analyze_trader_dna(
        statistics=statistics,
        risk=risk,
        consistency=consistency,
        psychology=psychology,
        behavior=behavior,
    )

    recommendations = generate_recommendations(
        risk=risk,
        behavior=behavior,
        psychology=psychology,
        consistency=consistency,
        strategies=consistency.get(
            "strategies",
            {},
        ),
        performance=performance,
    )

    return {
        "trades": trades,
        "statistics": statistics,
        "risk": risk,
        "behavior": behavior,
        "psychology": psychology,
        "performance": performance,
        "consistency": consistency,
        "trader_dna": trader_dna,
        "recommendations": recommendations,
    }
