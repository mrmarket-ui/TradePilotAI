"""
TradePilot AI analysis service.

Converts the unified intelligence pipeline output into typed
Pydantic response models.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from schemas.analysis.behavior import BehaviorAnalysis
from schemas.analysis.consistency import ConsistencyAnalysis
from schemas.analysis.performance import PerformanceAnalysis
from schemas.analysis.psychology import PsychologyAnalysis
from schemas.analysis.recommendation import Recommendation
from schemas.analysis.risk import RiskAnalysis
from schemas.analysis.trader_analysis import TraderAnalysis
from schemas.analysis.trader_dna import TraderDNAAnalysis

from services.analysis.pipeline import run_analysis_pipeline


class AnalysisService:
    """Public service for complete trader analysis."""

    @staticmethod
    def analyze(
        db: Session,
        user_id: int,
    ) -> TraderAnalysis:
        result = run_analysis_pipeline(
            db=db,
            user_id=user_id,
        )

        risk = result["risk"]
        behavior = result["behavior"]
        psychology = result["psychology"]
        performance = result["performance"]
        consistency = result["consistency"]
        trader_dna = result["trader_dna"]
        recommendations = result["recommendations"]

        return TraderAnalysis(
            risk=RiskAnalysis(
                maximum_drawdown=float(
                    risk.get(
                        "maximum_drawdown",
                        0,
                    )
                    or 0
                ),
                recovery_factor=float(
                    risk.get(
                        "recovery_factor",
                        0,
                    )
                    or 0
                ),
                expectancy=float(
                    risk.get(
                        "expectancy",
                        0,
                    )
                    or 0
                ),
            ),
            behavior=BehaviorAnalysis(
                **behavior
            ),
            psychology=PsychologyAnalysis(
                **psychology
            ),
            performance=PerformanceAnalysis(
                win_rate=performance[
                    "win_rate"
                ],
                profit_factor=performance[
                    "profit_factor"
                ],
                monthly_growth=performance[
                    "monthly_growth"
                ],
            ),
            consistency=ConsistencyAnalysis(
                score=consistency.get(
                    "score",
                    {},
                ),
                sessions=consistency.get(
                    "sessions",
                    {},
                ),
                symbols=consistency.get(
                    "symbols",
                    {},
                ),
                strategies=consistency.get(
                    "strategies",
                    {},
                ),
            ),
            trader_dna=TraderDNAAnalysis(
                **trader_dna
            ),
            recommendations=[
                Recommendation(**item)
                for item in recommendations
            ],
        )
