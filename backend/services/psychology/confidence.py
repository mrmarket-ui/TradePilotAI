def calculate_confidence_score(
    trades,
    consistency_trend="stable",
):
    """
    Confidence is based primarily on
    trading performance and recent trend.
    """

    if not trades:
        return 50

    wins = sum(
        1
        for t in trades
        if (t.profit or 0) > 0
    )

    win_rate = wins / len(trades)

    score = 50 + (win_rate * 40)

    if consistency_trend == "improving":
        score += 10

    elif consistency_trend == "declining":
        score -= 10

    return max(
        0,
        min(round(score), 100)
    )