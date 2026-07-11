from pydantic import BaseModel, Field


class ConsistencyAnalysis(BaseModel):
    score: dict = Field(default_factory=dict)
    sessions: dict = Field(default_factory=dict)
    symbols: dict = Field(default_factory=dict)
    strategies: dict = Field(default_factory=dict)
