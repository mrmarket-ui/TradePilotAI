from pydantic import BaseModel, Field


class MonthlyMetrics(BaseModel):
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    breakeven: int = 0
    win_rate: float = 0
    net_profit: float = 0
    profit_factor: float = 0
    average_win: float = 0
    average_loss: float = 0
    best_trade: float = 0
    worst_trade: float = 0


class MonthlyReviewResponse(BaseModel):
    period_start: str
    period_end: str
    grade: str
    score: float
    summary: str
    metrics: MonthlyMetrics
    trader_profile: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[dict] = Field(default_factory=list)
    next_month_mission: str
