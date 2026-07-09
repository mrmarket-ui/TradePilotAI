from services.recommendations.priority import (
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
)


def generate_consistency_recommendations(consistency):

    recommendations = []

    score = consistency.get(
        "score",
        {}
    ).get(
        "overall_score",
        100
    )

    trend = consistency.get(
        "trend",
        "Stable"
    )

    sessions = consistency.get(
        "sessions",
        {}
    )

    weekdays = consistency.get(
        "weekdays",
        {}
    )

    symbols = consistency.get(
        "symbols",
        {}
    )

    strategies = consistency.get(
        "strategies",
        {}
    )

    # ----------------------------------------
    # Overall Score
    # ----------------------------------------

    if score < 60:

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Consistency",

            "title": "Improve Consistency",

            "message":
                "Focus on following the same trading process every day."

        })

    elif score >= 85:

        recommendations.append({

            "priority": PRIORITY_LOW,

            "category": "Consistency",

            "title": "Excellent Consistency",

            "message":
                "Your trading consistency is excellent. Keep following your routine."

        })

    # ----------------------------------------
    # Trend
    # ----------------------------------------

    if trend == "Improving":

        recommendations.append({

            "priority": PRIORITY_LOW,

            "category": "Progress",

            "title": "Positive Progress",

            "message":
                "Your performance has improved over recent months."

        })

    elif trend == "Declining":

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Progress",

            "title": "Performance Declining",

            "message":
                "Review your recent trades to identify what's changed."

        })

    # ----------------------------------------
    # Best Session
    # ----------------------------------------

    if sessions:

        best = max(
            sessions,
            key=lambda s: sessions[s]["win_rate"]
        )

        recommendations.append({

            "priority": PRIORITY_MEDIUM,

            "category": "Session",

            "title": "Best Trading Session",

            "message":
                f"You perform best during the {best} session."

        })

    # ----------------------------------------
    # Best Weekday
    # ----------------------------------------

    if weekdays:

        best = max(
            weekdays,
            key=lambda d: weekdays[d]["win_rate"]
        )

        recommendations.append({

            "priority": PRIORITY_LOW,

            "category": "Weekday",

            "title": "Best Trading Day",

            "message":
                f"Your strongest trading day is {best}."

        })

    # ----------------------------------------
    # Best Symbol
    # ----------------------------------------

    if symbols:

        best = max(
            symbols,
            key=lambda s: symbols[s]["profit"]
        )

        recommendations.append({

            "priority": PRIORITY_MEDIUM,

            "category": "Markets",

            "title": "Best Market",

            "message":
                f"Your most profitable market is {best}."

        })

    # ----------------------------------------
    # Best Strategy
    # ----------------------------------------

    if strategies:

        best = max(
            strategies,
            key=lambda s: strategies[s]["profit"]
        )

        recommendations.append({

            "priority": PRIORITY_MEDIUM,

            "category": "Strategy",

            "title": "Best Strategy",

            "message":
                f"Continue focusing on your {best} strategy."

        })

    return recommendations
