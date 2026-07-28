from services.strategy_score import ScoreComponent
from services.strategy_score.normalize import normalize


def score_entry_rules(
    strategy,
    payload,
):
    required = {
        normalize(rule): rule
        for rule in (
            strategy.entry_rules or []
        )
    }

    observed = {
        normalize(rule): rule
        for rule in (
            payload.observed_entry_rules or []
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
        len(matched) / total * 20
        if total
        else 20
    )

    return ScoreComponent(
        name="Entry Rules",
        weight=20,
        earned=round(earned, 2),
        passed=len(missing) == 0,
        explanation=(
            f"{len(matched)}/{total} "
            "entry rules matched."
        ),
        matched=matched,
        missing=missing,
    )
