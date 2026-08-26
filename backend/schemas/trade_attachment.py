from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class TradeAttachmentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int
    trade_id: int

    attachment_type: str
    stage: str

    original_name: str
    stored_name: str

    mime_type: str | None = None
    file_size: int

    created_at: datetime


class TradeAttachmentListResponse(BaseModel):
    total: int
    attachments: list[
        TradeAttachmentResponse
    ]
