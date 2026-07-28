from services.strategy_score import ScoreComponent


def score_session(
    strategy,
    payload,
):
    allowed = strategy.sessions or []

    current = payload.session

    passed = current in allowed

    return ScoreComponent(
        name="Session",
        weight=10,
        earned=10 if passed else 0,
        passed=passed,
        explanation=(
            "Trading session matches."
            if passed
            else "Wrong trading session."
        ),
        matched=[current] if passed else [],
        missing=[] if passed else [current],
    )
