def _clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def calculate_consistency_score(

    statistics,
    risk,
    psychology,
    behavior,
    improvement

):

    score = 0

    breakdown = {}

    # ------------------------------------
    # Win Rate
    # ------------------------------------

    win_rate = statistics.get("win_rate", 0)

    win_score = _clamp(win_rate)

    breakdown["win_rate"] = round(win_score, 2)

    score += win_score * 0.20

    # ------------------------------------
    # Profitability
    # ------------------------------------

    profit_factor = statistics.get(
        "profit_factor",
        0
    )

    profit_score = _clamp(
        profit_factor * 50
    )

    breakdown["profitability"] = round(
        profit_score,
        2
    )

    score += profit_score * 0.20

    # ------------------------------------
    # Risk Management
    # ------------------------------------

    recovery = risk.get(
        "recovery_factor",
        0
    )

    risk_score = _clamp(
        recovery * 20
    )

    breakdown["risk"] = round(
        risk_score,
        2
    )

    score += risk_score * 0.15

    # ------------------------------------
    # Psychology
    # ------------------------------------

    psychology_score = psychology.get(
        "score",
        50
    )

    psychology_score = _clamp(
        psychology_score
    )

    breakdown["psychology"] = psychology_score

    score += psychology_score * 0.10

    # ------------------------------------
    # Behavior
    # ------------------------------------

    behavior_score = behavior.get(
        "score",
        50
    )

    behavior_score = _clamp(
        behavior_score
    )

    breakdown["behavior"] = behavior_score

    score += behavior_score * 0.10

    # ------------------------------------
    # Consistency
    # ------------------------------------

    consistency = statistics.get(
        "win_rate",
        0
    )

    consistency_score = _clamp(
        consistency
    )

    breakdown["consistency"] = consistency_score

    score += consistency_score * 0.15

    # ------------------------------------
    # Improvement
    # ------------------------------------

    trend = improvement

    if trend == "Improving":
        improvement_score = 100

    elif trend == "Mixed":
        improvement_score = 60

    elif trend == "Declining":
        improvement_score = 20

    else:
        improvement_score = 40

    breakdown["improvement"] = improvement_score

    score += improvement_score * 0.10

    return {

        "overall_score": round(score, 2),

        "grade": get_grade(score),

        "breakdown": breakdown

    }


def get_grade(score):

    if score >= 90:
        return "A+"

    if score >= 80:
        return "A"

    if score >= 70:
        return "B"

    if score >= 60:
        return "C"

    if score >= 50:
        return "D"

    return "F"
