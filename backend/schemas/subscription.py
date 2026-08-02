from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int
    provider: str
    plan: str
    status: str

    paypal_subscription_id: str | None = None
    paypal_plan_id: str | None = None
    payer_email: str | None = None

    currency: str
    amount: str | None = None
    next_billing_at: datetime | None = None

    created_at: datetime
    updated_at: datetime


class PublicPlanResponse(BaseModel):
    code: str
    name: str
    amount: str
    currency: str
    paypal_plan_id: str


class PlanCatalogueResponse(BaseModel):
    plans: list[PublicPlanResponse]


class PayPalSubscriptionCreateRequest(
    BaseModel
):
    plan: str = Field(
        min_length=3,
        max_length=20,
        examples=["pro"],
    )


class PayPalSubscriptionCreateResponse(
    BaseModel
):
    subscription_id: str
    status: str
    plan: str
    approval_url: str

class SubscriptionCancelResponse(
    BaseModel
):
    success: bool
    status: str
    plan: str
    message: str
