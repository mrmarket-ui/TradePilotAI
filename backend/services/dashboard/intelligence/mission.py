from __future__ import annotations

from typing import Any


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


def generate_mission(analysis: Any) -> dict:
    data = _to_dict(analysis)

    behavior = _to_dict(data.get("behavior"))
    performance = _to_dict(data.get("performance"))

    today = "Execute only trades that match your plan."
    week = "Maintain consistent execution across every session."

    if behavior.get("revenge_trading"):
        today = "Take zero revenge trades."
        week = (
            "Pause after every losing trade and avoid emotional re-entry."
        )

    elif behavior.get("fomo_detected"):
        today = "Do not chase price."
        week = "Wait for confirmed A+ entries only."

    elif performance.get("profit_factor", 0) < 1:
        today = "Take fewer but higher-quality setups."
        week = "Improve trade selection and protect capital."

    return {
        "today": today,
        "this_week": week,
    }
