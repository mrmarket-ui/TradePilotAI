from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class MT5TradeProposalCreate(BaseModel):
    broker_account_id: int
    strategy_profile_id: int

    symbol: str
    direction: str

    entry_price: float
    stop_loss: float
    take_profit: float

    risk_percent: float
    risk_reward: float

    max_hold_minutes: int = 30

    timeframe_context: Optional[dict[str, Any]] = None
    matched_rules: Optional[list[Any]] = None
    missing_rules: Optional[list[Any]] = None
    strategy_snapshot: Optional[dict[str, Any]] = None

    analysis_summary: Optional[str] = None

    expires_at: datetime


class MT5TradeProposalResponse(BaseModel):
    id: int
    user_id: int

    broker_account_id: int
    strategy_profile_id: Optional[int] = None

    symbol: str
    direction: str

    entry_price: float
    stop_loss: float
    take_profit: float

    risk_percent: float
    risk_reward: float

    max_hold_minutes: int

    timeframe_context: Optional[dict[str, Any]] = None
    matched_rules: Optional[list[Any]] = None
    missing_rules: Optional[list[Any]] = None
    strategy_snapshot: Optional[dict[str, Any]] = None

    analysis_summary: Optional[str] = None

    status: str

    expires_at: datetime
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
