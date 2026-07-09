from sqlalchemy.orm import Session

from models.trade import Trade

from schemas.analysis.trader_analysis import TraderAnalysis
from schemas.analysis.risk import RiskAnalysis
from schemas.analysis.behavior import BehaviorAnalysis
from schemas.analysis.psychology import PsychologyAnalysis
from schemas.analysis.performance import PerformanceAnalysis
from schemas.analysis.consistency import ConsistencyAnalysis

from services.analytics.engine import calculate_statistics
from services.analytics.risk import build_risk_summary

from services.consistency.engine import analyze_consistency
from services.behavior.engine import analyze_behavior


class AnalysisService:

    @staticmethod
    def load_trades(
        db: Session,
        user_id: int
    ):

        return (
            db.query(Trade)
            .filter(
                Trade.user_id == user_id
            )
            .all()
        )

    @staticmethod
    def analyze(
        db: Session,
        user_id: int
    ) -> TraderAnalysis:

        trades = AnalysisService.load_trades(
            db,
            user_id
        )

        statistics = calculate_statistics(
            db,
            user_id
        )

        risk = build_risk_summary(trades)

        #
        # Placeholder
        # These will become dedicated engines next.
        #

        behavior = analyze_behavior(trades)

        from services.psychology.engine import (
    analyze_psychology,
)
    psychology = analyze_psychology(
    trades,
    behavior,
    consistency["trend"],
)
        consistency = analyze_consistency(
            trades,
            statistics,
            risk,
            psychology,
            behavior,
        )

        return TraderAnalysis(

            risk=RiskAnalysis(

                maximum_drawdown=risk["maximum_drawdown"],
                recovery_factor=risk["recovery_factor"],
                expectancy=risk["expectancy"],

            ),

            behavior=BehaviorAnalysis(
                **behavior
            ),

            psychology=PsychologyAnalysis(
                **psychology
            ),

            performance=PerformanceAnalysis(

                win_rate=statistics["win_rate"],
                profit_factor=statistics["profit_factor"],
                monthly_growth=0,

            ),

            consistency=ConsistencyAnalysis(

                score=consistency["score"],
                sessions=consistency["sessions"],
                symbols=consistency["symbols"],
                strategies=consistency["strategies"],

            )

        )