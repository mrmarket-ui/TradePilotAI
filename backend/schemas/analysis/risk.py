from pydantic import BaseModel


class RiskAnalysis(BaseModel):
    maximum_drawdown: float = 0.0
    recovery_factor: float = 0.0
    expectancy: float = 0.0