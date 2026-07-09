from pydantic import BaseModel


class BehaviorAnalysis(BaseModel):

    revenge_trading: bool = False

    fomo_detected: bool = False

    holding_losers_too_long: bool = False

    cutting_winners_too_early: bool = False

    position_size_discipline: bool = True

    strategy_discipline: bool = True

    session_discipline: bool = True

    weekend_trading: bool = False