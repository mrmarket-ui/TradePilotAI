from services.behavior.revenge import detect_revenge_trading
from services.behavior.fomo import detect_fomo
from services.behavior.holding import analyze_holding_behavior
from services.behavior.discipline import (
    analyze_position_size,
    analyze_strategy_discipline,
    analyze_session_discipline,
)
from services.behavior.weekend import detect_weekend_trading


def analyze_behavior(trades):

    holding = analyze_holding_behavior(trades)

    return {

        "revenge_trading":
            detect_revenge_trading(trades),

        "fomo_detected":
            detect_fomo(trades),

        "holding_losers_too_long":
            holding["holding_losers_too_long"],

        "cutting_winners_too_early":
            holding["cutting_winners_too_early"],

        "position_size_discipline":
            analyze_position_size(trades),

        "strategy_discipline":
            analyze_strategy_discipline(trades),

        "session_discipline":
            analyze_session_discipline(trades),

        "weekend_trading":
            detect_weekend_trading(trades),
    }