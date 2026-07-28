from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScoreComponent:
    name: str
    weight: float
    earned: float
    passed: bool
    explanation: str
    matched: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)


@dataclass
class StrategyScoreResult:
    overall_score: float
    verdict: str
    confidence: float
    components: list[ScoreComponent]
    strengths: list[str]
    weaknesses: list[str]
    recommendation: str
    metadata: dict[str, Any] = field(default_factory=dict)
