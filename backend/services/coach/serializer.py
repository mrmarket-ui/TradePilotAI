"""
TradePilot AI Serializer
------------------------

Combines every AI module into one
clean API response.
"""


def build_ai_response(
    score=None,
    statistics=None,
    risk=None,
    psychology=None,
    consistency=None,
    behavior=None,
    strengths=None,
    weaknesses=None,
    insights=None,
    recommendations=None,
):

    return {

        "tradepilot": score or {},

        "statistics": statistics or {},

        "risk": risk or {},

        "psychology": psychology or {},

        "consistency": consistency or {},

        "behavior": behavior or {},

        "strengths": strengths or [],

        "weaknesses": weaknesses or [],

        "insights": insights or [],

        "recommendations": recommendations or []

    }