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


def generate_headline(analysis: Any) -> dict:
    data = _to_dict(analysis)

    behavior = _to_dict(data.get("behavior"))
    performance = _to_dict(data.get("performance"))
    trader_dna = _to_dict(data.get("trader_dna"))

    if behavior.get("revenge_trading"):
        return {
            "title": "Execution Needs Attention",
            "message": (
                "Your biggest opportunity is eliminating revenge trading."
            ),
        }

    if behavior.get("fomo_detected"):
        return {
            "title": "Patience Is Your Edge",
            "message": (
                "Wait for planned entries instead of chasing price."
            ),
        }

    if performance.get("profit_factor", 0) < 1:
        return {
            "title": "Protect Your Capital",
            "message": (
                "Your losses currently outweigh your gains. "
                "Focus on fewer, higher-quality setups."
            ),
        }

    return {
        "title": trader_dna.get(
            "profile",
            "Developing Trader",
        ),
        "message": (
            "Keep reinforcing disciplined execution and consistent risk."
        ),
    }
