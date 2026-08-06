from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
)


class StrategyUrlCreate(BaseModel):
    url: HttpUrl


class StrategySourceResponse(BaseModel):
    id: int
    source_type: str
    original_name: str | None
    source_url: str | None
    mime_type: str | None
    status: str
    extracted_strategy: dict | None
    error_message: str | None
    created_at: datetime
    analyzed_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class StrategyExtractionResponse(BaseModel):
    source_id: int
    status: str
    strategy: dict


class CreateStrategyFromSourceRequest(BaseModel):
    name: str | None = Field(
        default=None,
        max_length=120,
    )
