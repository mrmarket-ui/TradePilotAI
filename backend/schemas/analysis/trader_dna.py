from pydantic import BaseModel, Field


class TraderDNAAnalysis(BaseModel):
    profile: str
    overall_score: float
    personality: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    sufficient_data: bool = True
    trades_recorded: int = 0
    trades_needed: int = 0
