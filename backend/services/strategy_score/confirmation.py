from services.strategy_score import ScoreComponent
from services.strategy_score.normalize import normalize


def score_confirmations(
    strategy,
    payload,
):
    required = {
        normalize(rule): rule
        for rule in (
            strategy.confirmations or []
        )
    }

    observed = {
        normalize(rule): rule
        for rule in (
            payload.observed_confirmations or []
        )
    }

    matched_keys = (
        required.keys()
        & observed.keys()
    )

    missing_keys = (
        required.keys()
        - observed.keys()
    )

    matched = sorted(
        required[key]
        for key in matched_keys
    )

    missing = sorted(
        required[key]
        for key in missing_keys
    )

    total = len(required)

    earned = (
        len(matched) / total * 15
        if total
        else 15
    )

    return ScoreComponent(
        name="Confirmations",
        weight=15,
        earned=round(earned, 2),
        passed=len(missing) == 0,
        explanation=(
            f"{len(matched)}/{total} "
            "confirmations matched."
        ),
        matched=matched,
        missing=missing,
    )
