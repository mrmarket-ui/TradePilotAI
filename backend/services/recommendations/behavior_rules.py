from services.recommendations.priority import (
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
)


def generate_behavior_recommendations(behavior):

    recommendations = []

    # Revenge Trading

    if behavior.get("revenge_trading", False):

        recommendations.append({

            "priority": PRIORITY_CRITICAL,

            "category": "Behavior",

            "title": "Stop Revenge Trading",

            "message": (
                "You frequently enter new trades immediately after losses. "
                "Take a short break after losing trades."
            )

        })

    # FOMO

    if behavior.get("fomo_detected", False):

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Behavior",

            "title": "Reduce FOMO",

            "message": (
                "You often chase moves after they have already happened. "
                "Wait for planned entries."
            )

        })

    # Holding losers

    if behavior.get("holding_losers_too_long", False):

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Behavior",

            "title": "Cut Losing Trades Earlier",

            "message": (
                "Losing trades remain open significantly longer than winners."
            )

        })

    # Cutting winners

    if behavior.get("cutting_winners_too_early", False):

        recommendations.append({

            "priority": PRIORITY_MEDIUM,

            "category": "Behavior",

            "title": "Let Winners Run",

            "message": (
                "Profitable trades are being closed too early."
            )

        })

    # Position sizing

    if not behavior.get("position_size_discipline", True):

        recommendations.append({

            "priority": PRIORITY_HIGH,

            "category": "Behavior",

            "title": "Improve Position Sizing",

            "message": (
                "Your position sizes are inconsistent. "
                "Risk a fixed percentage on every trade."
            )

        })

    # Strategy discipline

    if not behavior.get("strategy_discipline", True):

        recommendations.append({

            "priority": PRIORITY_MEDIUM,

            "category": "Behavior",

            "title": "Stick To Your Strategy",

            "message": (
                "Avoid switching strategies too frequently."
            )

        })

    # Session discipline

    if not behavior.get("session_discipline", True):

        recommendations.append({

            "priority": PRIORITY_LOW,

            "category": "Behavior",

            "title": "Trade Your Best Session",

            "message": (
                "Your results are stronger during specific market sessions."
            )

        })

    # Weekend trading

    if behavior.get("weekend_trading", False):

        recommendations.append({

            "priority": PRIORITY_LOW,

            "category": "Behavior",

            "title": "Avoid Weekend Trading",

            "message": (
                "Weekend trading often increases unnecessary risk."
            )

        })

    return recommendations
