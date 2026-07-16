from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TradeBase(BaseModel):
    broker: str | None = None
    ticket: str | None = None

    pair: str = Field(
        min_length=1,
        max_length=30,
    )

    direction: str = Field(
        min_length=1,
        max_length=10,
    )

    entry: float
    exit_price: float | None = None

    stop_loss: float
    take_profit: float

    lot_size: float | None = Field(
        default=None,
        ge=0,
    )

    profit: float | None = None
    commission: float = 0
    swap: float = 0

    magic_number: int | None = None
    comment: str | None = None

    strategy: str | None = None
    emotion: str | None = None
    notes: str | None = None

    opened_at: datetime | None = None
    closed_at: datetime | None = None

    imported: bool = False


class TradeCreate(TradeBase):
    pass


class TradeUpdate(BaseModel):
    broker: str | None = None
    ticket: str | None = None

    pair: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )

    direction: str | None = Field(
        default=None,
        min_length=1,
        max_length=10,
    )

    entry: float | None = None
    exit_price: float | None = None

    stop_loss: float | None = None
    take_profit: float | None = None

    lot_size: float | None = Field(
        default=None,
        ge=0,
    )

    profit: float | None = None
    commission: float | None = None
    swap: float | None = None

    magic_number: int | None = None
    comment: str | None = None

    strategy: str | None = None
    emotion: str | None = None
    notes: str | None = None

    opened_at: datetime | None = None
    closed_at: datetime | None = None

    imported: bool | None = None


class TradeResponse(TradeBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int
    created_at: datetime


class TradeListResponse(BaseModel):
    total: int
    trades: list[TradeResponse]
