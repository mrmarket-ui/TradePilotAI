from datetime import datetime
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    review: str | None = Field(
        default=None,
        max_length=2000,
    )


class OfferCreate(BaseModel):
    partner_id: int
    title: str = Field(max_length=200)
    description: str | None = None
    coupon_code: str | None = None
    offer_url: str | None = None
    active: bool = True
    expires_at: datetime | None = None


class OfferUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    coupon_code: str | None = None
    offer_url: str | None = None
    active: bool | None = None
    expires_at: datetime | None = None
