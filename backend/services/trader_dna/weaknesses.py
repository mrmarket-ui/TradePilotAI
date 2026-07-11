"""
TradePilot AI

Trader DNA Weakness Analysis
"""


def identify_weaknesses(

    psychology,
    behavior,

):

    weaknesses = []

    if behavior.get("revenge_trading"):
        weaknesses.append("Revenge trading")

    if behavior.get("fomo_detected"):
        weaknesses.append("FOMO entries")

    if behavior.get("holding_losers_too_long"):
        weaknesses.append("Holds losing trades too long")

    if behavior.get("cutting_winners_too_early"):
        weaknesses.append("Cuts winners too early")

    if not behavior.get("position_size_discipline", True):
        weaknesses.append("Inconsistent position sizing")

    if not behavior.get("strategy_discipline", True):
        weaknesses.append("Strategy hopping")

    if psychology.get("fear_score", 0) > 60:
        weaknesses.append("Fear affects execution")

    if psychology.get("greed_score", 0) > 60:
        weaknesses.append("Greed affects decisions")

    if psychology.get("stress_score", 0) > 70:
        weaknesses.append("High trading stress")

    return weaknesses