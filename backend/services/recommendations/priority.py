PRIORITY_CRITICAL = "Critical"
PRIORITY_HIGH = "High"
PRIORITY_MEDIUM = "Medium"
PRIORITY_LOW = "Low"


def priority_value(priority):

    values = {
        PRIORITY_CRITICAL: 4,
        PRIORITY_HIGH: 3,
        PRIORITY_MEDIUM: 2,
        PRIORITY_LOW: 1,
    }

    return values.get(priority, 0)


def sort_recommendations(recommendations):

    return sorted(

        recommendations,

        key=lambda recommendation: priority_value(
            recommendation["priority"]
        ),

        reverse=True

    )
