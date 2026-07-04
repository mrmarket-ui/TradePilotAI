from pydantic import BaseModel


class ConnectBroker(BaseModel):
    broker: str
    server: str
    account_number: int
    password: str


class BrokerResponse(BaseModel):
    id: int
    broker: str
    server: str
    account_number: str
    connected: bool

    class Config:
        from_attributes = True