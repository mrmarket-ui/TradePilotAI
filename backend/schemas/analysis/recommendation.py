from pydantic import BaseModel


class Recommendation(BaseModel):

    priority: str

    category: str

    title: str

    message: str