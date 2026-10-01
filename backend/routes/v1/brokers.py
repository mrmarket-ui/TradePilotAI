from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.subscription import require_premium_plan
from models.user import User
from models.broker_account import BrokerAccount
from models.strategy_profile import StrategyProfile

from schemas.broker import (
    AutoTraderSettings,
    BrokerResponse,
    ConnectBroker,
    LinkBrokerStrategy,
)
from services.brokers.mt5 import (
    connect,
    disconnect,
)
from services.security.encryption import encrypt


router = APIRouter(
    prefix="/brokers",
    tags=["Brokers"],
)


@router.get(
    "",
    response_model=list[BrokerResponse],
)
def list_broker_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    return (
        db.query(BrokerAccount)
        .filter(
            BrokerAccount.user_id == current_user.id
        )
        .order_by(BrokerAccount.id.asc())
        .all()
    )


@router.post(
    "/connect",
    response_model=BrokerResponse,
)
def connect_broker(
    broker: ConnectBroker,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    success, message = connect(
        broker.account_number,
        broker.password,
        broker.server,
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail=str(message),
        )

    try:
        existing = (
            db.query(BrokerAccount)
            .filter(
                BrokerAccount.user_id == current_user.id,
                BrokerAccount.account_number
                == str(broker.account_number),
                BrokerAccount.server == broker.server,
            )
            .first()
        )

        if existing:
            existing.broker = broker.broker
            existing.encrypted_password = encrypt(
                broker.password
            )
            existing.connected = True

            db.commit()
            db.refresh(existing)

            return existing

        account = BrokerAccount(
            user_id=current_user.id,
            broker=broker.broker,
            server=broker.server,
            account_number=str(
                broker.account_number
            ),
            encrypted_password=encrypt(
                broker.password
            ),
            connected=True,
        )

        db.add(account)
        db.commit()
        db.refresh(account)

        return account

    finally:
        disconnect()


@router.patch(
    "/{account_id}/strategy",
    response_model=BrokerResponse,
)
def link_strategy(
    account_id: int,
    payload: LinkBrokerStrategy,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    account = (
        db.query(BrokerAccount)
        .filter(
            BrokerAccount.id == account_id,
            BrokerAccount.user_id == current_user.id,
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="MT5 account not found.",
        )

    strategy = (
        db.query(StrategyProfile)
        .filter(
            StrategyProfile.id
            == payload.strategy_profile_id,
            StrategyProfile.user_id
            == current_user.id,
        )
        .first()
    )

    if not strategy:
        raise HTTPException(
            status_code=404,
            detail="Strategy Brain strategy not found.",
        )

    if strategy.is_archived:
        raise HTTPException(
            status_code=400,
            detail=(
                "Archived strategies cannot be linked "
                "to MT5."
            ),
        )

    if not strategy.is_active:
        raise HTTPException(
            status_code=400,
            detail=(
                "The Strategy Brain strategy must be "
                "active before it can be linked to MT5."
            ),
        )

    # Changing the Strategy Brain strategy invalidates the
    # current AutoTrader monitoring configuration. The trader
    # must explicitly enable AutoTrader again for the new strategy.
    account.autotrader_enabled = False
    account.strategy_profile_id = strategy.id

    db.commit()
    db.refresh(account)

    return account


@router.delete(
    "/{account_id}/strategy",
    response_model=BrokerResponse,
)
def unlink_strategy(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    account = (
        db.query(BrokerAccount)
        .filter(
            BrokerAccount.id == account_id,
            BrokerAccount.user_id == current_user.id,
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="MT5 account not found.",
        )

    # AutoTrader cannot remain enabled without a linked strategy.
    account.autotrader_enabled = False
    account.strategy_profile_id = None

    db.commit()
    db.refresh(account)

    return account


@router.post(
    "/{account_id}/autotrader/enable",
    response_model=BrokerResponse,
)
def enable_autotrader(
    account_id: int,
    payload: AutoTraderSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    account = (
        db.query(BrokerAccount)
        .filter(
            BrokerAccount.id == account_id,
            BrokerAccount.user_id == current_user.id,
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="MT5 account not found.",
        )

    if not account.connected:
        raise HTTPException(
            status_code=400,
            detail=(
                "MT5 account must be connected before "
                "AutoTrader can be enabled."
            ),
        )

    if account.strategy_profile_id is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Link an active Strategy Brain strategy "
                "before enabling AutoTrader."
            ),
        )

    strategy = (
        db.query(StrategyProfile)
        .filter(
            StrategyProfile.id
            == account.strategy_profile_id,
            StrategyProfile.user_id
            == current_user.id,
        )
        .first()
    )

    if not strategy:
        raise HTTPException(
            status_code=404,
            detail="Linked Strategy Brain strategy not found.",
        )

    if strategy.is_archived:
        raise HTTPException(
            status_code=400,
            detail=(
                "Archived strategies cannot be used "
                "by AutoTrader."
            ),
        )

    if not strategy.is_active:
        raise HTTPException(
            status_code=400,
            detail=(
                "The linked Strategy Brain strategy "
                "must be active."
            ),
        )

    markets = strategy.markets or []

    normalized_markets = {
        str(market).strip().lower()
        for market in markets
    }

    if "forex" not in normalized_markets:
        raise HTTPException(
            status_code=400,
            detail=(
                "AutoTrader is restricted to Forex strategies. "
                "The linked Strategy Brain strategy must include "
                "Forex in its markets."
            ),
        )
    if not strategy.requires_user_approval:
        raise HTTPException(
            status_code=400,
            detail=(
                "Trader approval must be enabled in "
                "Strategy Brain before AutoTrader "
                "can be activated."
            ),
        )

    if payload.max_hold_minutes not in (30, 60):
        raise HTTPException(
            status_code=400,
            detail=(
                "Maximum holding time must be "
                "30 or 60 minutes."
            ),
        )

    account.autotrader_enabled = True
    account.max_hold_minutes = (
        payload.max_hold_minutes
    )

    db.commit()
    db.refresh(account)

    return account


@router.post(
    "/{account_id}/autotrader/disable",
    response_model=BrokerResponse,
)
def disable_autotrader(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    account = (
        db.query(BrokerAccount)
        .filter(
            BrokerAccount.id == account_id,
            BrokerAccount.user_id == current_user.id,
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="MT5 account not found.",
        )

    account.autotrader_enabled = False

    db.commit()
    db.refresh(account)

    return account

@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_broker_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    account = (
        db.query(BrokerAccount)
        .filter(
            BrokerAccount.id == account_id,
            BrokerAccount.user_id == current_user.id,
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="MT5 account not found.",
        )

    db.delete(account)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )





