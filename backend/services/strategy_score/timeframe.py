from services.strategy_score import ScoreComponent


def score_timeframe(
    strategy,
    payload,
):
    allowed = strategy.timeframes or []

    current = payload.timeframe

    passed = current in allowed

    return ScoreComponent(
        name="Timeframe",
        weight=10,
        earned=10 if passed else 0,
        passed=passed,
        explanation=(
            "Correct timeframe."
            if passed
            else "Timeframe not allowed."
        ),
        matched=[current] if passed else [],
        missing=[] if passed else [current],
    )
