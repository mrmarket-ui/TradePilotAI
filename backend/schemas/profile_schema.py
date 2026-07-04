from datetime import datetime
from pydantic import BaseModel, EmailStr


class ProfileResponse(BaseModel):
    id: int
    email: EmailStr

    full_name: str | None = None
    username: str | None = None
    avatar: str | None = None
    bio: str | None = None

    plan: str
    ai_credits: int
    is_admin: bool

    created_at: datetime

    class Config:
        from_attributes = True