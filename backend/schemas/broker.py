from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ConnectBroker(BaseModel):
    broker: str
    server: str
    account_number: int
    password: str


class LinkBrokerStrategy(BaseModel):
    strategy_profile_id: int


class AutoTraderSettings(BaseModel):
    max_hold_minutes: int = 30


class BrokerResponse(BaseModel):
    id: int
    broker: str
    server: str
    account_number: str
    connected: bool
    last_sync: Optional[datetime] = None
    strategy_profile_id: Optional[int] = None
    autotrader_enabled: bool = False
    max_hold_minutes: int = 30

    class Config:
        from_attributes = True


