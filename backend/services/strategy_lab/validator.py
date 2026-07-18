from schemas.strategy_profile import (
    StrategyProfileCreate,
    StrategyProfileUpdate,
)


def validate_strategy_create(
    payload: StrategyProfileCreate,
) -> None:
    if not payload.markets:
        raise ValueError(
            "At least one market is required."
        )

    if not payload.timeframes:
        raise ValueError(
            "At least one timeframe is required."
        )

    if not payload.entry_rules:
        raise ValueError(
            "At least one entry rule is required."
        )


def validate_strategy_update(
    payload: StrategyProfileUpdate,
) -> None:
    data = payload.model_dump(
        exclude_unset=True,
    )

    for field in (
        "markets",
        "timeframes",
        "entry_rules",
    ):
        value = data.get(field)

        if (
            field in data
            and value is not None
            and len(value) == 0
        ):
            readable_name = (
                field
                .replace("_", " ")
                .title()
            )

            raise ValueError(
                f"{readable_name} cannot be empty."
            )
