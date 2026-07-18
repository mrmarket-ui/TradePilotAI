from models.strategy_profile import (
    StrategyProfile,
)

from schemas.strategy_profile import (
    SetupScoreRequest,
    SetupScoreResponse,
)

from services.strategy_lab.scorer import (
    score_setup,
)


def evaluate_setup(
    strategy: StrategyProfile,
    payload: SetupScoreRequest,
) -> SetupScoreResponse:
    return score_setup(
        strategy=strategy,
        payload=payload,
    )
