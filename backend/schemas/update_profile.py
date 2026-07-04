from pydantic import BaseModel


class UpdateProfile(BaseModel):
    full_name: str | None = None
    username: str | None = None
    bio: str | None = None
    avatar: str | None = None