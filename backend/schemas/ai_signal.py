from pydantic import (
    BaseModel,
    Field,
)


class PaperTradeCreate(BaseModel):
    signal_id: int
    entry_price: float
    risk_percent: float = Field(
        default=0.5,
        gt=0,
        le=10,
    )


class PaperTradeClose(BaseModel):
    exit_price: float


class SignalApproval(BaseModel):
    approved: bool
