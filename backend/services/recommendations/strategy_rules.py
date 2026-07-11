from services.recommendations.priority import (
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
)


def generate_strategy_recommendations(
    strategies: dict,
) -> list[dict]:
    recommendations = []

    valid = {
        name: data
        for name, data in strategies.items()
        if (
            name
            and name.strip().lower() != "unspecified"
            and data.get("trades", 0) >= 3
        )
    }

    if not valid:
        recommendations.append({
            "priority": PRIORITY_MEDIUM,
            "category": "Strategy",
            "title": "Label Your Trading Strategies",
            "message": (
                "Add a strategy name to each trade so TradePilot AI "
                "can identify which setups are profitable."
            ),
        })

        return recommendations

    profitable = {
        name: data
        for name, data in valid.items()
        if data.get("profit", 0) > 0
    }

    losing = {
        name: data
        for name, data in valid.items()
        if data.get("profit", 0) < 0
    }

    if profitable:
        best_name = max(
            profitable,
            key=lambda name: profitable[name].get("profit", 0),
        )
        best = profitable[best_name]

        recommendations.append({
            "priority": PRIORITY_LOW,
            "category": "Strategy",
            "title": "Focus On Your Strength",
            "message": (
                f"{best_name} is currently your strongest strategy "
                f"with a profit of {best['profit']:.2f}."
            ),
        })

    if losing:
        worst_name = min(
            losing,
            key=lambda name: losing[name].get("profit", 0),
        )

        recommendations.append({
            "priority": PRIORITY_HIGH,
            "category": "Strategy",
            "title": "Review Weak Strategy",
            "message": (
                f"{worst_name} has produced losses. Review or pause "
                f"this strategy until its execution improves."
            ),
        })

    return recommendations
