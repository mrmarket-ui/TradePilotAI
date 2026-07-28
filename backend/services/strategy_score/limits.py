from services.strategy_score import ScoreComponent


def score_limits(
    strategy,
    payload,
):
    passed = (
        payload.trades_today
        < strategy.max_trades_per_day
        and
        payload.consecutive_losses
        <= strategy.max_consecutive_losses
    )

    return ScoreComponent(
        name="Daily Limits",
        weight=10,
        earned=10 if passed else 0,
        passed=passed,
        explanation=(
            "Trading limits respected."
            if passed
            else "Daily limits exceeded."
        ),
        matched=[],
        missing=[],
    )
