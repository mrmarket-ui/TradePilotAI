from fastapi import APIRouter
from fastapi import FastAPI

from database.database import Base, engine

from models.user import User
from models.trade import Trade
from models.broker_account import BrokerAccount

from routes.v1 import health, auth, profile, brokers

from routes.v1.trading import (
    sync,
    analytics,
    signals,
    memory
)
router = APIRouter(
    prefix="/trades",
    tags=["Trades"]
)


@router.get("/")
def get_trades():
    return {"message": "Trades endpoint"}