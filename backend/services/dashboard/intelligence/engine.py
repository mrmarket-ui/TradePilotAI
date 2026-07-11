from __future__ import annotations

from typing import Any

from services.dashboard.intelligence.headline import (
    generate_headline,
)
from services.dashboard.intelligence.mission import (
    generate_mission,
)
from services.dashboard.intelligence.scorecard import (
    generate_scorecard,
)
from services.dashboard.intelligence.alerts import (
    generate_alerts,
)


def _to_dict(value: Any) -> dict:
    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    return {}


def generate_dashboard_intelligence(
    analysis: Any,
) -> dict:
    data = _to_dict(analysis)

    risk = _to_dict(data.get("risk"))
    performance = _to_dict(data.get("performance"))

    return {
        "headline": generate_headline(analysis),
        "mission": generate_mission(analysis),
        "scorecard": generate_scorecard(analysis),
        "alerts": generate_alerts(analysis),
        "quick_stats": {
            "win_rate": float(
                performance.get("win_rate", 0) or 0
            ),
            "profit_factor": float(
                performance.get("profit_factor", 0) or 0
            ),
            "expectancy": float(
                risk.get("expectancy", 0) or 0
            ),
            "maximum_drawdown": float(
                risk.get("maximum_drawdown", 0) or 0
            ),
        },
    }
