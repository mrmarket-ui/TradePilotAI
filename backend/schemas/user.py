from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)
    full_name: str | None = Field(default=None, max_length=80)
    accept_terms: bool = False
