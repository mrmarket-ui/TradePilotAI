from pydantic import BaseModel, Field


class TradeReviewResponse(BaseModel):
    trade_score: float = Field(
        ge=0,
        le=100,
    )

    summary: str

    strengths: list[str] = Field(
        default_factory=list
    )

    mistakes: list[str] = Field(
        default_factory=list
    )

    lesson: str

    next_mission: str
