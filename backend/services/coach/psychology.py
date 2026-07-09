"""
TradePilot AI
Psychology Engine
"""

from services.coach.behavior import (
    detect_overtrading,
    detect_revenge_trading,
    detect_fomo,
    detect_holding_losers,
    detect_cutting_winners,
    detect_position_sizing,
    detect_strategy_discipline,
)


def analyze_psychology(trades):

    return {

        "overall_score": psychology_score(trades),

        "discipline": discipline_score(trades),

        "patience": patience_score(trades),

        "confidence": confidence_score(trades),

        "fear": fear_score(trades),

        "greed": greed_score(trades),

        "emotional_control": emotional_control_score(trades),

        "consistency": consistency_score(trades),

    }

# ==========================================================
# Overall Psychology Score
# ==========================================================

def psychology_score(trades):

    score = 100

    if detect_overtrading(trades)["detected"]:
        score -= 10

    if detect_revenge_trading(trades)["detected"]:
        score -= 15

    if detect_fomo(trades)["detected"]:
        score -= 15

    if detect_holding_losers(trades)["detected"]:
        score -= 15

    if detect_cutting_winners(trades)["detected"]:
        score -= 10

    if detect_position_sizing(trades)["detected"]:
        score -= 15

    if detect_strategy_discipline(trades)["detected"]:
        score -= 10

    return max(score, 0)

