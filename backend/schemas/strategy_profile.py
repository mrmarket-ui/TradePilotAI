from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class StrategyProfileBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=120,
    )

    description: str | None = None

    markets: list[str] = Field(
        default_factory=list,
    )

    sessions: list[str] = Field(
        default_factory=list,
    )

    timeframes: list[str] = Field(
        default_factory=list,
    )

    entry_rules: list[str] = Field(
        default_factory=list,
    )

    exit_rules: list[str] = Field(
        default_factory=list,
    )

    confirmations: list[str] = Field(
        default_factory=list,
    )

    psychology_rules: list[str] = Field(
        default_factory=list,
    )

    trade_management_rules: list[str] = Field(
        default_factory=list,
    )

    max_risk_percent: float = Field(
        default=0.5,
        gt=0,
        le=10,
    )

    max_daily_loss_percent: float = Field(
        default=2.0,
        gt=0,
        le=25,
    )

    max_weekly_loss_percent: float = Field(
        default=5.0,
        gt=0,
        le=50,
    )

    max_trades_per_day: int = Field(
        default=3,
        ge=1,
        le=100,
    )

    max_consecutive_losses: int = Field(
        default=2,
        ge=1,
        le=20,
    )

    requires_user_approval: bool = True

    @field_validator(
        "markets",
        "sessions",
        "timeframes",
        "entry_rules",
        "exit_rules",
        "confirmations",
        "psychology_rules",
        "trade_management_rules",
    )
    @classmethod
    def normalize_list(
        cls,
        value: list[str],
    ) -> list[str]:
        normalized: list[str] = []

        for item in value:
            clean = item.strip()

            if clean and clean not in normalized:
                normalized.append(clean)

        return normalized


class StrategyProfileCreate(
    StrategyProfileBase
):
    is_active: bool = False


class StrategyProfileUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
    )

    description: str | None = None

    markets: list[str] | None = None
    sessions: list[str] | None = None
    timeframes: list[str] | None = None

    entry_rules: list[str] | None = None
    exit_rules: list[str] | None = None
    confirmations: list[str] | None = None

    psychology_rules: list[str] | None = None
    trade_management_rules: list[str] | None = None

    max_risk_percent: float | None = Field(
        default=None,
        gt=0,
        le=10,
    )

    max_daily_loss_percent: float | None = Field(
        default=None,
        gt=0,
        le=25,
    )

    max_weekly_loss_percent: float | None = Field(
        default=None,
        gt=0,
        le=50,
    )

    max_trades_per_day: int | None = Field(
        default=None,
        ge=1,
        le=100,
    )

    max_consecutive_losses: int | None = Field(
        default=None,
        ge=1,
        le=20,
    )

    requires_user_approval: bool | None = None
    is_active: bool | None = None


class StrategyProfileResponse(
    StrategyProfileBase
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class StrategyListResponse(BaseModel):
    total: int
    strategies: list[StrategyProfileResponse]


class SetupScoreRequest(BaseModel):
    market: str = Field(
        min_length=1,
        max_length=30,
    )

    session: str | None = None
    timeframe: str | None = None

    observed_entry_rules: list[str] = Field(
        default_factory=list,
    )

    observed_confirmations: list[str] = Field(
        default_factory=list,
    )

    risk_percent: float = Field(
        gt=0,
        le=100,
    )

    consecutive_losses: int = Field(
        default=0,
        ge=0,
    )

    trades_today: int = Field(
        default=0,
        ge=0,
    )

    user_emotion: str | None = None


class SetupScoreResponse(BaseModel):
    strategy_id: int
    strategy_name: str

    overall_score: float
    verdict: str

    matched_rules: list[str]
    missing_rules: list[str]

    matched_confirmations: list[str]
    missing_confirmations: list[str]

    risk_passed: bool
    psychology_passed: bool
    daily_limit_passed: bool

    explanation: str
