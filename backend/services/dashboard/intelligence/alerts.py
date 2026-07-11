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


def generate_alerts(analysis: Any) -> list[dict]:
    data = _to_dict(analysis)

    recommendations = data.get(
        "recommendations",
        [],
    )

    alerts = []

    for item in recommendations:
        item = _to_dict(item)

        priority = item.get("priority", "Low")

        if priority not in {
            "Critical",
            "High",
        }:
            continue

        alerts.append({
            "priority": priority,
            "category": item.get("category", "General"),
            "title": item.get("title", "Trading Alert"),
            "message": item.get("message", ""),
        })

        if len(alerts) >= 5:
            break

    return alerts
