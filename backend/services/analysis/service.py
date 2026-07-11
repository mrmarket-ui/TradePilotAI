"""
TradePilot AI unified analysis service.

Runs the complete intelligence pipeline for an authenticated trader.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from schemas.analysis.behavior import BehaviorAnalysis
from schemas.analysis.consistency import ConsistencyAnalysis
from schemas.analysis.performance import PerformanceAnalysis
from schemas.analysis.psychology import PsychologyAnalysis
from schemas.analysis.recommendation import Recommendation
from schemas.analysis.risk import RiskAnalysis
from schemas.analysis.trader_analysis import TraderAnalysis
from schemas.analysis.trader_dna import TraderDNAAnalysis

from services.analysis.loader import load_user_trades
from services.analytics.engine import calculate_statistics
from services.analytics.risk import build_risk_summary
from services.behavior.engine import analyze_behavior
from services.consistency.engine import analyze_consistency
from services.psychology.engine import analyze_psychology
from services.recommendations.engine import generate_recommendations
from services.trader_dna.engine import analyze_trader_dna


def _monthly_growth(consistency: dict[str, Any]) -> float:
    monthly = consistency.get("monthly_progress", {})

    if len(monthly) < 2:
        return 0.0

    ordered_months = sorted(monthly.keys())
    previous_profit = float(
        monthly[ordered_months[-2]].get("profit", 0) or 0
    )
    current_profit = float(
        monthly[ordered_months[-1]].get("profit", 0) or 0
    )

    if previous_profit == 0:
        return 100.0 if current_profit > 0 else 0.0

    growth = (
        (current_profit - previous_profit)
        / abs(previous_profit)
    ) * 100

    return round(growth, 2)


def _consistency_score(consistency: dict[str, Any]) -> float:
    score = consistency.get("score", {})

    if isinstance(score, dict):
        return float(score.get("overall_score", 0) or 0)

    return float(score or 0)


class AnalysisService:
    """Central orchestration service for trader intelligence."""

    @staticmethod
    def analyze(
        db: Session,
        user_id: int,
    ) -> TraderAnalysis:
        trades = load_user_trades(
            db=db,
            user_id=user_id,
        )

        statistics = calculate_statistics(
            db=db,
            user_id=user_id,
        )

        risk = build_risk_summary(trades)
        behavior = analyze_behavior(trades)

        # First psychology pass avoids a circular dependency.
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

        monthly_growth = _monthly_growth(consistency)
        consistency_score = _consistency_score(consistency)

        performance = {
            "trend": consistency.get("trend", "Stable"),
            "monthly_growth": monthly_growth,
            "win_rate": float(statistics.get("win_rate", 0) or 0),
            "profit_factor": float(
                statistics.get("profit_factor", 0) or 0
            ),
            "consistency_score": consistency_score,
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
            strategies=consistency.get("strategies", {}),
            performance=performance,
        )

        return TraderAnalysis(
            risk=RiskAnalysis(
                maximum_drawdown=float(
                    risk.get("maximum_drawdown", 0) or 0
                ),
                recovery_factor=float(
                    risk.get("recovery_factor", 0) or 0
                ),
                expectancy=float(
                    risk.get("expectancy", 0) or 0
                ),
            ),
            behavior=BehaviorAnalysis(**behavior),
            psychology=PsychologyAnalysis(**psychology),
            performance=PerformanceAnalysis(
                win_rate=performance["win_rate"],
                profit_factor=performance["profit_factor"],
                monthly_growth=performance["monthly_growth"],
            ),
            consistency=ConsistencyAnalysis(
                score=consistency.get("score", {}),
                sessions=consistency.get("sessions", {}),
                symbols=consistency.get("symbols", {}),
                strategies=consistency.get("strategies", {}),
            ),
            trader_dna=TraderDNAAnalysis(**trader_dna),
            recommendations=[
                Recommendation(**item)
                for item in recommendations
            ],
        )
