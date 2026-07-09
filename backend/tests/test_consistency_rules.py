from services.recommendations.consistency_rules import (
    generate_consistency_recommendations
)

consistency = {

    "score": {
        "overall_score": 91
    },

    "trend": "Improving",

    "sessions": {

        "London": {
            "win_rate": 78
        },

        "New York": {
            "win_rate": 55
        }

    },

    "weekdays": {

        "Tuesday": {
            "win_rate": 82
        },

        "Friday": {
            "win_rate": 41
        }

    },

    "symbols": {

        "XAUUSD": {
            "profit": 5200
        },

        "EURUSD": {
            "profit": 1700
        }

    },

    "strategies": {

        "Liquidity Sweep": {
            "profit": 6100
        },

        "Breakout": {
            "profit": 1400
        }

    }

}

recommendations = generate_consistency_recommendations(
    consistency
)

for recommendation in recommendations:

    print(recommendation)
