def calculate_discipline_score(
    behavior,
):
    """
    Starts at 100 and deducts
    points for poor habits.
    """

    score = 100

    penalties = {

        "revenge_trading": 20,

        "fomo_detected": 15,

        "holding_losers_too_long": 15,

        "cutting_winners_too_early": 10,

        "weekend_trading": 10,

    }

    for key, penalty in penalties.items():

        if behavior.get(key):

            score -= penalty

    if not behavior.get(
        "position_size_discipline",
        True
    ):
        score -= 15

    if not behavior.get(
        "strategy_discipline",
        True
    ):
        score -= 10

    if not behavior.get(
        "session_discipline",
        True
    ):
        score -= 5

    return max(score, 0)