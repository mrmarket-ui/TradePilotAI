from pydantic import BaseModel, Field


class AIChatResponse(BaseModel):
    answer: str
    suggestions: list[str] = Field(
        default_factory=list
    )
