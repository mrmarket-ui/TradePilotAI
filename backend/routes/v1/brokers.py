from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from models.broker_account import BrokerAccount

from schemas.broker import ConnectBroker, BrokerResponse

from services.brokers.mt5 import login, shutdown
from services.security.encryption import encrypt

router = APIRouter(
    prefix="/brokers",
    tags=["Brokers"]
)


@router.post(
    "/connect",
    response_model=BrokerResponse
)
def connect_broker(
    broker: ConnectBroker,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    success, message = login(
    broker.account_number,
    broker.password,
    broker.server
)

    if not success:
        raise HTTPException(
            status_code=400,
            detail=str(message)
        )

    account = BrokerAccount(
        user_id=current_user.id,
        broker=broker.broker,
        server=broker.server,
        account_number=str(broker.account_number),
        encrypted_password=encrypt(
            broker.password
        ),
        connected=True
    )

    db.add(account)
    db.commit()
    db.refresh(account)
    return account
    shutdown()