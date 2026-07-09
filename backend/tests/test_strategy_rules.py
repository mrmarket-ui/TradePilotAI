from services.recommendations.strategy_rules import (
    generate_strategy_recommendations
)

strategies = {

    "Liquidity Sweep": {

        "profit": 8200

    },

    "Breakout": {

        "profit": -1200

    },

    "SMC Continuation": {

        "profit": 2400

    }

}

recommendations = generate_strategy_recommendations(
    strategies
)

for recommendation in recommendations:

    print(recommendation)
