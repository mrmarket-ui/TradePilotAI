from pydantic import BaseModel


class PsychologyAnalysis(BaseModel):

    discipline_score: float = 100

    confidence_score: float = 100

    emotional_control: float = 100

    stress_score: float = 0

    greed_score: float = 0

    fear_score: float = 0