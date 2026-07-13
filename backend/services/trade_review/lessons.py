"""
TradePilot AI Trade Review Lesson Generator.
"""


def generate_trade_lesson(
    mistakes: list[str],
) -> str:
    if not mistakes:
        return (
            "Continue repeating the same disciplined process "
            "while documenting every decision."
        )

    first = mistakes[0]

    lesson_map = {
        "No stop loss was recorded":
            "Define the maximum acceptable loss before entering every trade.",

        "No take-profit target was recorded":
            "Set a clear profit objective before opening the position.",

        "The trading strategy was not labelled":
            "Label every trade so the system can measure which setups work.",

        "Position size was not recorded":
            "Record position size so risk discipline can be evaluated.",

        "The stop-loss distance is invalid":
            "Check entry and stop-loss values before executing the trade.",

        "The planned reward was smaller than the risk":
            "Avoid trades where the expected reward is smaller than the risk.",

        "The trade closed at a loss":
            "Review whether the loss came from the strategy or poor execution.",
    }

    return lesson_map.get(
        first,
        "Review the trade objectively and identify one execution rule to improve.",
    )
