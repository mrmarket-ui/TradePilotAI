"""
TradePilot AI Trade Review Mission Generator.
"""


def generate_next_mission(
    mistakes: list[str],
) -> str:
    if not mistakes:
        return (
            "Repeat this process for your next three trades "
            "without breaking your trading rules."
        )

    first = mistakes[0]

    mission_map = {
        "No stop loss was recorded":
            "Record a stop loss before entering each of your next five trades.",

        "No take-profit target was recorded":
            "Set a take-profit target before each of your next five entries.",

        "The trading strategy was not labelled":
            "Label the strategy used on your next ten trades.",

        "Position size was not recorded":
            "Record position size on every trade this week.",

        "The stop-loss distance is invalid":
            "Validate entry and stop-loss values before your next five trades.",

        "The planned reward was smaller than the risk":
            "Only take trades with at least a 1.5-to-1 planned reward-to-risk ratio.",

        "The trade closed at a loss":
            "Review the setup before placing another trade and avoid emotional re-entry.",
    }

    return mission_map.get(
        first,
        "Apply one clear improvement rule to your next five trades.",
    )
