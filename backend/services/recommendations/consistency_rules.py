from services.recommendations.priority import (
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
)


def generate_consistency_recommendations(consistency: dict) -> list[dict]:
    recommendations = []

    score_data = consistency.get("score", {})
    score = (
        score_data.get("overall_score", 0)
        if isinstance(score_data, dict)
        else float(score_data or 0)
    )

    trend = consistency.get("trend", "Stable")
    sessions = consistency.get("sessions", {})
    weekdays = consistency.get("weekdays", {})
    symbols = consistency.get("symbols", {})
    strategies = consistency.get("strategies", {})

    if score < 60:
        recommendations.append({
            "priority": PRIORITY_HIGH,
            "category": "Consistency",
            "title": "Improve Consistency",
            "message": (
                "Focus on following the same trading process every day."
            ),
        })
    elif score >= 85:
        recommendations.append({
            "priority": PRIORITY_LOW,
            "category": "Consistency",
            "title": "Excellent Consistency",
            "message": (
                "Your trading consistency is excellent. "
                "Keep following your routine."
            ),
        })

    if trend == "Improving":
        recommendations.append({
            "priority": PRIORITY_LOW,
            "category": "Progress",
            "title": "Positive Progress",
            "message": (
                "Your performance has improved over recent months."
            ),
        })
    elif trend == "Declining":
        recommendations.append({
            "priority": PRIORITY_HIGH,
            "category": "Progress",
            "title": "Performance Declining",
            "message": (
                "Review your recent trades to identify what changed."
            ),
        })

    profitable_sessions = {
        name: data
        for name, data in sessions.items()
        if (
            data.get("trades", 0) >= 3
            and data.get("profit", 0) > 0
        )
    }

    if profitable_sessions:
        best_session = max(
            profitable_sessions,
            key=lambda name: profitable_sessions[name].get("profit", 0),
        )

        recommendations.append({
            "priority": PRIORITY_MEDIUM,
            "category": "Session",
            "title": "Best Trading Session",
            "message": (
                f"You currently perform best during the "
                f"{best_session} session."
            ),
        })

    profitable_weekdays = {
        name: data
        for name, data in weekdays.items()
        if (
            data.get("trades", 0) >= 3
            and data.get("profit", 0) > 0
        )
    }

    if profitable_weekdays:
        best_day = max(
            profitable_weekdays,
            key=lambda name: profitable_weekdays[name].get("profit", 0),
        )

        recommendations.append({
            "priority": PRIORITY_LOW,
            "category": "Weekday",
            "title": "Best Trading Day",
            "message": (
                f"Your strongest profitable trading day is {best_day}."
            ),
        })

    profitable_symbols = {
        name: data
        for name, data in symbols.items()
        if (
            data.get("trades", 0) >= 3
            and data.get("profit", 0) > 0
        )
    }

    if profitable_symbols:
        best_symbol = max(
            profitable_symbols,
            key=lambda name: profitable_symbols[name].get("profit", 0),
        )

        recommendations.append({
            "priority": PRIORITY_MEDIUM,
            "category": "Markets",
            "title": "Best Market",
            "message": (
                f"Your most profitable market is {best_symbol}."
            ),
        })

    valid_strategies = {
        name: data
        for name, data in strategies.items()
        if (
            name.strip().lower() != "unspecified"
            and data.get("trades", 0) >= 3
            and data.get("profit", 0) > 0
        )
    }

    if valid_strategies:
        best_strategy = max(
            valid_strategies,
            key=lambda name: valid_strategies[name].get("profit", 0),
        )

        recommendations.append({
            "priority": PRIORITY_MEDIUM,
            "category": "Strategy",
            "title": "Best Strategy",
            "message": (
                f"Continue focusing on your {best_strategy} strategy."
            ),
        })

    return recommendations
