from pydantic import BaseModel, field_validator


SUPPORTED_LANGUAGES = {
    "en",
    "af",
    "fr",
    "es",
    "pt",
    "de",
    "ar",
    "zh",
    "ja",
}


SUPPORTED_CURRENCIES = {
    "USD",
    "ZAR",
    "EUR",
    "GBP",
    "CAD",
    "AUD",
    "JPY",
    "CNY",
    "INR",
    "NGN",
    "AED",
}


class UpdateProfile(BaseModel):
    full_name: str | None = None
    username: str | None = None
    bio: str | None = None
    avatar: str | None = None

    preferred_language: str | None = None
    preferred_currency: str | None = None

    @field_validator("preferred_language")
    @classmethod
    def validate_language(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        clean_value = value.strip().lower()

        if clean_value not in SUPPORTED_LANGUAGES:
            raise ValueError(
                "Unsupported language."
            )

        return clean_value

    @field_validator("preferred_currency")
    @classmethod
    def validate_currency(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        clean_value = value.strip().upper()

        if clean_value not in SUPPORTED_CURRENCIES:
            raise ValueError(
                "Unsupported currency."
            )

        return clean_value
