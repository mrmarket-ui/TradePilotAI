from services.strategy_score import ScoreComponent


def score_risk(
    strategy,
    payload,
):
    passed = (
        payload.risk_percent
        <= strategy.max_risk_percent
    )

    return ScoreComponent(
        name="Risk",
        weight=10,
        earned=10 if passed else 0,
        passed=passed,
        explanation=(
            "Risk within strategy."
            if passed
            else "Risk exceeds strategy maximum."
        ),
        matched=[
            f"{payload.risk_percent}%"
        ] if passed else [],
        missing=[] if passed else [
            f"Max {strategy.max_risk_percent}%"
        ],
    )
