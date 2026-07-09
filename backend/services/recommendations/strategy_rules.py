from services.recommendations.priority import (
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
)


def generate_strategy_recommendations(strategies):

    recommendations = []

    if not strategies:
        return recommendations

    best_strategy = max(
        strategies,
        key=lambda strategy: strategies[strategy]["profit"]
    )

    worst_strategy = min(
        strategies,
        key=lambda strategy: strategies[strategy]["profit"]
    )

    best = strategies[best_strategy]
    worst = strategies[worst_strategy]

    recommendations.append({

        "priority": PRIORITY_LOW,

        "category": "Strategy",

        "title": "Focus On Your Strength",

        "message":
            f"{best_strategy} is currently your strongest strategy with a profit of {best['profit']:.2f}."

    })

    if worst["profit"] < 0:

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Strategy",

            "title": "Review Weak Strategy",

            "message":
                f"{worst_strategy} has produced losses. Review or stop using it until improvements are made."

        })

    elif worst["profit"] < best["profit"] * 0.25:

        recommendations.append({

            "priority": PRIORITY_MEDIUM,

            "category": "Strategy",

            "title": "Improve Strategy Selection",

            "message":
                f"{worst_strategy} is significantly underperforming compared to your best strategy."

        })

    return recommendations
