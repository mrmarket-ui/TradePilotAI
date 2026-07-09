from services.recommendations.priority import (
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
)


def generate_performance_recommendations(performance):

    recommendations = []

    trend = performance.get(
        "trend",
        "Stable"
    )

    monthly_growth = performance.get(
        "monthly_growth",
        0
    )

    win_rate = performance.get(
        "win_rate",
        0
    )

    profit_factor = performance.get(
        "profit_factor",
        0
    )

    consistency = performance.get(
        "consistency_score",
        0
    )

    # ----------------------------------------
    # Performance Trend
    # ----------------------------------------

    if trend == "Improving":

        recommendations.append({

            "priority": PRIORITY_LOW,

            "category": "Performance",

            "title": "Excellent Progress",

            "message":
                "Your trading performance has steadily improved."

        })

    elif trend == "Declining":

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Performance",

            "title": "Performance Declining",

            "message":
                "Your recent trading performance is declining. Review your recent trades."

        })

    # ----------------------------------------
    # Monthly Growth
    # ----------------------------------------

    if monthly_growth > 20:

        recommendations.append({

            "priority": PRIORITY_LOW,

            "category": "Growth",

            "title": "Strong Monthly Growth",

            "message":
                "Excellent monthly growth. Continue following your trading plan."

        })

    elif monthly_growth < 0:

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Growth",

            "title": "Negative Monthly Growth",

            "message":
                "Your account has declined this month. Reduce risk and review mistakes."

        })

    # ----------------------------------------
    # Win Rate
    # ----------------------------------------

    if win_rate >= 70:

        recommendations.append({

            "priority": PRIORITY_LOW,

            "category": "Performance",

            "title": "High Win Rate",

            "message":
                "Your win rate is excellent. Maintain your current execution."

        })

    elif win_rate < 50:

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Performance",

            "title": "Improve Win Rate",

            "message":
                "Focus on taking higher-quality trade setups."

        })

    # ----------------------------------------
    # Profit Factor
    # ----------------------------------------

    if profit_factor >= 2:

        recommendations.append({

            "priority": PRIORITY_LOW,

            "category": "Performance",

            "title": "Strong Trading Edge",

            "message":
                "Your profit factor indicates a healthy trading edge."

        })

    elif profit_factor < 1:

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Performance",

            "title": "Weak Trading Edge",

            "message":
                "Your profit factor is below 1. Focus on improving your strategy."

        })

    # ----------------------------------------
    # Consistency
    # ----------------------------------------

    if consistency >= 85:

        recommendations.append({

            "priority": PRIORITY_LOW,

            "category": "Consistency",

            "title": "Highly Consistent",

            "message":
                "Excellent consistency. Keep following your routine."

        })

    elif consistency < 60:

        recommendations.append({

            "priority": PRIORITY_MEDIUM,

            "category": "Consistency",

            "title": "Consistency Needs Work",

            "message":
                "Aim to trade the same way every day."

        })

    return recommendations
