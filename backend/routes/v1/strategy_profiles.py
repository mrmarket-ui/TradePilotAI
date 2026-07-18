from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.user import User

from schemas.strategy_profile import (
    SetupScoreRequest,
    SetupScoreResponse,
    StrategyListResponse,
    StrategyProfileCreate,
    StrategyProfileResponse,
    StrategyProfileUpdate,
)

from services.strategy_lab.crud import (
    activate_strategy,
    create_strategy,
    delete_strategy,
    get_strategy,
    list_strategies,
    update_strategy,
)

from services.strategy_lab.engine import (
    evaluate_setup,
)

from services.strategy_lab.validator import (
    validate_strategy_create,
    validate_strategy_update,
)


router = APIRouter(
    prefix="/strategies",
    tags=["Strategy Brain"],
)


def get_owned_strategy(
    db: Session,
    user_id: int,
    strategy_id: int,
):
    strategy = get_strategy(
        db=db,
        user_id=user_id,
        strategy_id=strategy_id,
    )

    if strategy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found.",
        )

    return strategy


@router.post(
    "",
    response_model=StrategyProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_strategy_profile(
    payload: StrategyProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        validate_strategy_create(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return create_strategy(
        db=db,
        user_id=current_user.id,
        payload=payload,
    )


@router.get(
    "",
    response_model=StrategyListResponse,
)
def read_strategy_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategies = list_strategies(
        db=db,
        user_id=current_user.id,
    )

    return {
        "total": len(strategies),
        "strategies": strategies,
    }


@router.get(
    "/{strategy_id}",
    response_model=StrategyProfileResponse,
)
def read_strategy_profile(
    strategy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_strategy(
        db=db,
        user_id=current_user.id,
        strategy_id=strategy_id,
    )


@router.patch(
    "/{strategy_id}",
    response_model=StrategyProfileResponse,
)
def patch_strategy_profile(
    strategy_id: int,
    payload: StrategyProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        validate_strategy_update(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    strategy = get_owned_strategy(
        db=db,
        user_id=current_user.id,
        strategy_id=strategy_id,
    )

    return update_strategy(
        db=db,
        strategy=strategy,
        payload=payload,
    )


@router.delete(
    "/{strategy_id}",
)
def remove_strategy_profile(
    strategy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = get_owned_strategy(
        db=db,
        user_id=current_user.id,
        strategy_id=strategy_id,
    )

    delete_strategy(
        db=db,
        strategy=strategy,
    )

    return {
        "success": True,
        "message": "Strategy deleted.",
        "strategy_id": strategy_id,
    }


@router.post(
    "/{strategy_id}/activate",
    response_model=StrategyProfileResponse,
)
def activate_strategy_profile(
    strategy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = get_owned_strategy(
        db=db,
        user_id=current_user.id,
        strategy_id=strategy_id,
    )

    return activate_strategy(
        db=db,
        strategy=strategy,
    )


@router.post(
    "/{strategy_id}/score",
    response_model=SetupScoreResponse,
)
def score_strategy_setup(
    strategy_id: int,
    payload: SetupScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = get_owned_strategy(
        db=db,
        user_id=current_user.id,
        strategy_id=strategy_id,
    )

    return evaluate_setup(
        strategy=strategy,
        payload=payload,
    )
