def calculate_coach_score(analysis: dict) -> dict:
    """
    Calculate the overall AI Coach score (0-100)
    and convert it into a letter grade.
    """

    score = 100

    # -------------------------------
    # Risk
    # -------------------------------

    risk = analysis.get("risk", {})

    if risk.get("maximum_drawdown", 0) > 1000:
        score -= 10

    if risk.get("recovery_factor", 2) < 1:
        score -= 10

    if risk.get("expectancy", 1) < 0:
        score -= 10

    # -------------------------------
    # Psychology
    # -------------------------------

    psychology = analysis.get("psychology", {})

    if psychology.get("discipline_score", 100) < 60:
        score -= 10

    if psychology.get("stress_score", 0) > 70:
        score -= 10

    if psychology.get("greed_score", 0) > 70:
        score -= 5

    if psychology.get("fear_score", 0) > 70:
        score -= 5

    # -------------------------------
    # Behavior
    # -------------------------------

    behavior = analysis.get("behavior", {})

    if behavior.get("revenge_trading"):
        score -= 10

    if behavior.get("fomo_detected"):
        score -= 5

    if behavior.get("holding_losers_too_long"):
        score -= 5

    if behavior.get("cutting_winners_too_early"):
        score -= 5

    if not behavior.get("position_size_discipline", True):
        score -= 5

    # -------------------------------
    # Consistency
    # -------------------------------

    consistency = analysis.get("consistency", {})

    consistency_score = (
        consistency.get("score", {})
        .get("overall_score", 100)
    )

    if consistency_score < 80:
        score -= 10

    elif consistency_score < 90:
        score -= 5

    # -------------------------------
    # Performance
    # -------------------------------

    performance = analysis.get("performance", {})

    if performance.get("profit_factor", 2) < 1:
        score -= 10

    if performance.get("win_rate", 100) < 50:
        score -= 10

    # Clamp score

    score = max(0, min(100, score))

    # -------------------------------
    # Grade
    # -------------------------------

    if score >= 97:
        grade = "A+"

    elif score >= 93:
        grade = "A"

    elif score >= 90:
        grade = "A-"

    elif score >= 87:
        grade = "B+"

    elif score >= 83:
        grade = "B"

    elif score >= 80:
        grade = "B-"

    elif score >= 75:
        grade = "C+"

    elif score >= 70:
        grade = "C"

    elif score >= 60:
        grade = "D"

    else:
        grade = "F"

    return {
        "score": score,
        "grade": grade,
    }
