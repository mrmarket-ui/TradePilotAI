"""
TradePilot AI

Trader DNA Classifier

Determines the trader profile
using the intelligence engines.

Author:
TradePilot AI
"""


def classify_trader(

    statistics,
    risk,
    consistency,
    psychology,
    behavior,

):

    consistency_score = consistency.get(
        "score",
        50
    )

    confidence = psychology.get(
        "confidence_score",
        50
    )

    discipline = psychology.get(
        "discipline_score",
        50
    )

    emotion = psychology.get(
        "emotional_control",
        50
    )

    win_rate = statistics.get(
        "win_rate",
        50
    )

    risk_score = risk.get(
        "risk_score",
        50
    )

    # ------------------------------------------------

    if (

        discipline >= 90

        and

        consistency_score >= 90

        and

        emotion >= 85

    ):

        return "Elite Professional"

    # ------------------------------------------------

    if (

        discipline >= 80

        and

        consistency_score >= 80

    ):

        return "Disciplined Professional"

    # ------------------------------------------------

    if (

        win_rate >= 65

        and

        risk_score >= 70

    ):

        return "Precision Swing Trader"

    # ------------------------------------------------

    if (

        behavior.get(
            "revenge_trading",
            False
        )

        or

        psychology.get(
            "stress_score",
            0
        ) > 70

    ):

        return "Emotional Trader"

    # ------------------------------------------------

    if psychology.get(
        "fear_score",
        0
    ) > 60:

        return "Fearful Trader"

    # ------------------------------------------------

    if psychology.get(
        "greed_score",
        0
    ) > 60:

        return "Aggressive Trader"

    # ------------------------------------------------

    if consistency_score < 50:

        return "Developing Trader"

    # ------------------------------------------------

    return "Balanced Trader"