def calculate_emotional_scores(
    behavior,
):
    """
    Derive greed, fear and emotional
    control from trading behaviour.
    """

    greed = 0

    fear = 0

    emotional_control = 100

    if behavior.get("revenge_trading"):

        greed += 20
        emotional_control -= 20

    if behavior.get("fomo_detected"):

        greed += 25
        emotional_control -= 15

    if behavior.get("cutting_winners_too_early"):

        fear += 25

    if behavior.get("holding_losers_too_long"):

        fear += 15
        emotional_control -= 15

    return {

        "greed_score": min(greed, 100),

        "fear_score": min(fear, 100),

        "emotional_control": max(
            emotional_control,
            0
        )

    }