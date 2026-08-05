from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class PartnerBase(BaseModel):
    name: str
    slug: str
    category: str

    description: str | None = None
    referral_url: str

    badge: str | None = None
    logo_url: str | None = None

    status: str = "active"
    featured: bool = False
    display_order: int = 0

    minimum_deposit: str | None = None
    platforms: list[str] | None = None
    demo_available: bool | None = None
    regulation: str | None = None

    challenge_size: str | None = None
    challenge_fee: str | None = None
    profit_split: str | None = None
    max_drawdown: str | None = None
    payout_frequency: str | None = None


class PartnerCreate(PartnerBase):
    pass


class PartnerUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    category: str | None = None
    description: str | None = None
    referral_url: str | None = None
    badge: str | None = None
    logo_url: str | None = None
    status: str | None = None
    featured: bool | None = None
    display_order: int | None = None

    minimum_deposit: str | None = None
    platforms: list[str] | None = None
    demo_available: bool | None = None
    regulation: str | None = None

    challenge_size: str | None = None
    challenge_fee: str | None = None
    profit_split: str | None = None
    max_drawdown: str | None = None
    payout_frequency: str | None = None


class PartnerResponse(PartnerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class PartnerClickRequest(BaseModel):
    source: str = Field(
        default="partners_page",
        max_length=80,
    )


class PartnerAnalyticsItem(BaseModel):
    partner_id: int
    name: str
    category: str
    clicks: int


class PartnerAnalyticsResponse(BaseModel):
    total_clicks: int
    total_partners: int
    active_partners: int
    saved_count: int
    partners: list[PartnerAnalyticsItem]
