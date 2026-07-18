from sqlalchemy.orm import Session

from models.strategy_profile import (
    StrategyProfile,
)

from schemas.strategy_profile import (
    StrategyProfileCreate,
    StrategyProfileUpdate,
)


def deactivate_all_strategies(
    db: Session,
    user_id: int,
) -> None:
    (
        db.query(StrategyProfile)
        .filter(
            StrategyProfile.user_id
            == user_id
        )
        .update(
            {
                StrategyProfile.is_active:
                    False
            },
            synchronize_session=False,
        )
    )

    db.flush()


def create_strategy(
    db: Session,
    user_id: int,
    payload: StrategyProfileCreate,
) -> StrategyProfile:
    if payload.is_active:
        deactivate_all_strategies(
            db=db,
            user_id=user_id,
        )

    strategy = StrategyProfile(
        user_id=user_id,
        **payload.model_dump(),
    )

    db.add(strategy)
    db.commit()
    db.refresh(strategy)

    return strategy


def list_strategies(
    db: Session,
    user_id: int,
) -> list[StrategyProfile]:
    return (
        db.query(StrategyProfile)
        .filter(
            StrategyProfile.user_id
            == user_id
        )
        .order_by(
            StrategyProfile.is_active.desc(),
            StrategyProfile.updated_at.desc(),
        )
        .all()
    )


def get_strategy(
    db: Session,
    user_id: int,
    strategy_id: int,
) -> StrategyProfile | None:
    return (
        db.query(StrategyProfile)
        .filter(
            StrategyProfile.id
            == strategy_id,
            StrategyProfile.user_id
            == user_id,
        )
        .first()
    )


def update_strategy(
    db: Session,
    strategy: StrategyProfile,
    payload: StrategyProfileUpdate,
) -> StrategyProfile:
    updates = payload.model_dump(
        exclude_unset=True,
    )

    if updates.get("is_active") is True:
        deactivate_all_strategies(
            db=db,
            user_id=strategy.user_id,
        )

    for field, value in updates.items():
        setattr(
            strategy,
            field,
            value,
        )

    db.commit()
    db.refresh(strategy)

    return strategy


def delete_strategy(
    db: Session,
    strategy: StrategyProfile,
) -> None:
    db.delete(strategy)
    db.commit()


def activate_strategy(
    db: Session,
    strategy: StrategyProfile,
) -> StrategyProfile:
    deactivate_all_strategies(
        db=db,
        user_id=strategy.user_id,
    )

    strategy.is_active = True

    db.commit()
    db.refresh(strategy)

    return strategy
