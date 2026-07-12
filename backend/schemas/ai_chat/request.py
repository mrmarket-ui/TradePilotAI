from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=2,
        max_length=2000,
    )
