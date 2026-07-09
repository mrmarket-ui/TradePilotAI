from services.recommendations.priority import (
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
)


def generate_risk_recommendations(risk):

    recommendations = []

    drawdown = risk.get(
        "maximum_drawdown",
        0
    )

    recovery = risk.get(
        "recovery_factor",
        0
    )

    expectancy = risk.get(
        "expectancy",
        0
    )

    # -------------------------------
    # Drawdown
    # -------------------------------

    if drawdown > 1000:

        recommendations.append({

            "priority": PRIORITY_CRITICAL,

            "category": "Risk",

            "title": "Reduce Drawdown",

            "message": (
                "Your drawdown is becoming excessive. "
                "Reduce your position size and preserve capital."
            )

        })

    elif drawdown > 500:

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Risk",

            "title": "Monitor Drawdown",

            "message": (
                "Your drawdown is increasing. "
                "Review recent losing trades."
            )

        })

    # -------------------------------
    # Recovery Factor
    # -------------------------------

    if recovery < 1:

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Risk",

            "title": "Improve Recovery",

            "message": (
                "Your recovery factor is below 1. "
                "Focus on consistency before increasing risk."
            )

        })

    # -------------------------------
    # Expectancy
    # -------------------------------

    if expectancy < 0:

        recommendations.append({

            "priority": PRIORITY_CRITICAL,

            "category": "Risk",

            "title": "Negative Expectancy",

            "message": (
                "Your trading system currently has a negative expectancy. "
                "Review your strategy before placing new trades."
            )

        })

    elif expectancy < 10:

        recommendations.append({

            "priority": PRIORITY_MEDIUM,

            "category": "Risk",

            "title": "Increase Edge",

            "message": (
                "Your expectancy is positive but relatively low. "
                "Work on improving your average reward-to-risk ratio."
            )

        })

    return recommendations
