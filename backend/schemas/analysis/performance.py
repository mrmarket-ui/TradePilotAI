from pydantic import BaseModel


class PerformanceAnalysis(BaseModel):

    win_rate: float = 0

    profit_factor: float = 0

    monthly_growth: float = 0