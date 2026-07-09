from services.recommendations.behavior_rules import (
    generate_behavior_recommendations
)

behavior = {

    "revenge_trading": True,

    "fomo_detected": True,

    "holding_losers_too_long": True,

    "cutting_winners_too_early": True,

    "position_size_discipline": False,

    "strategy_discipline": False,

    "session_discipline": False,

    "weekend_trading": True

}

recommendations = generate_behavior_recommendations(behavior)

for recommendation in recommendations:

    print(recommendation)
