def calculate_stress_score(
    behavior,
):
    """
    Estimates stress from
    behavioural patterns.
    """

    stress = 0

    if behavior.get("revenge_trading"):
        stress += 30

    if behavior.get("fomo_detected"):
        stress += 20

    if behavior.get(
        "holding_losers_too_long"
    ):
        stress += 20

    if behavior.get(
        "weekend_trading"
    ):
        stress += 10

    return min(stress, 100)