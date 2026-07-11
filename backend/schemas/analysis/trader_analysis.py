from pydantic import BaseModel

from schemas.analysis.risk import RiskAnalysis
from schemas.analysis.behavior import BehaviorAnalysis
from schemas.analysis.psychology import PsychologyAnalysis
from schemas.analysis.performance import PerformanceAnalysis
from schemas.analysis.consistency import ConsistencyAnalysis
from schemas.analysis.trader_dna import TraderDNAAnalysis
from schemas.analysis.recommendation import Recommendation


class TraderAnalysis(BaseModel):

    risk: RiskAnalysis

    behavior: BehaviorAnalysis

    psychology: PsychologyAnalysis

    performance: PerformanceAnalysis

    consistency: ConsistencyAnalysis

    trader_dna: TraderDNAAnalysis

    recommendations: list[Recommendation]