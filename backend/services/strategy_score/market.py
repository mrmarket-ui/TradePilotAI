from services.strategy_score import ScoreComponent


def score_market(
    strategy,
    payload,
):
    allowed = strategy.markets or []

    current = payload.market

    passed = current in allowed

    return ScoreComponent(
        name="Market",
        weight=15,
        earned=15 if passed else 0,
        passed=passed,
        explanation=(
            f"{current} is allowed."
            if passed
            else f"{current} is not part of this strategy."
        ),
        matched=[current] if passed else [],
        missing=[] if passed else [current],
    )
