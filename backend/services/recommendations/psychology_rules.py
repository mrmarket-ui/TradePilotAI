from services.recommendations.priority import (
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
)


def generate_psychology_recommendations(psychology):

    recommendations = []

    confidence = psychology.get(
        "confidence_score",
        100
    )

    discipline = psychology.get(
        "discipline_score",
        100
    )

    emotional = psychology.get(
        "emotional_control",
        100
    )

    greed = psychology.get(
        "greed_score",
        0
    )

    fear = psychology.get(
        "fear_score",
        0
    )

    stress = psychology.get(
        "stress_score",
        0
    )

    # -----------------------------------
    # Confidence
    # -----------------------------------

    if confidence < 40:

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Psychology",

            "title": "Rebuild Confidence",

            "message":
                "Your confidence is very low. Reduce risk and rebuild consistency."

        })

    elif confidence > 95:

        recommendations.append({

            "priority": PRIORITY_MEDIUM,

            "category": "Psychology",

            "title": "Avoid Overconfidence",

            "message":
                "High confidence can lead to unnecessary risk. Stay disciplined."

        })

    # -----------------------------------
    # Discipline
    # -----------------------------------

    if discipline < 60:

        recommendations.append({

            "priority": PRIORITY_CRITICAL,

            "category": "Psychology",

            "title": "Improve Discipline",

            "message":
                "Your discipline score is low. Follow your trading plan strictly."

        })

    # -----------------------------------
    # Emotional Control
    # -----------------------------------

    if emotional < 60:

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Psychology",

            "title": "Control Emotions",

            "message":
                "Emotions are affecting your trading decisions."

        })

    # -----------------------------------
    # Greed
    # -----------------------------------

    if greed > 70:

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Psychology",

            "title": "Manage Greed",

            "message":
                "Avoid increasing risk after winning trades."

        })

    # -----------------------------------
    # Fear
    # -----------------------------------

    if fear > 70:

        recommendations.append({

            "priority": PRIORITY_MEDIUM,

            "category": "Psychology",

            "title": "Reduce Fear",

            "message":
                "Fear is preventing you from executing your trading plan."

        })

    # -----------------------------------
    # Stress
    # -----------------------------------

    if stress > 80:

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Psychology",

            "title": "Take a Break",

            "message":
                "High stress negatively impacts decision-making."

        })

    if not recommendations:

        recommendations.append({

            "priority": PRIORITY_LOW,

            "category": "Psychology",

            "title": "Psychology Stable",

            "message":
                "Your psychological profile is healthy. Maintain your routine."

        })

    return recommendations
