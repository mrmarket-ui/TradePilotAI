"""
TradePilot AI Scoring Engine
----------------------------
Calculates the overall TradePilot Score (0–1000)

Categories:
- Analytics
- Risk
- Psychology
- Consistency
- Behavior

Final score is normalized to 1000.
"""


def calculate_tradepilot_score(
    statistics: dict,
    risk: dict,
    psychology: dict = None,
    consistency: dict = None,
    behavior: dict = None,
):

    psychology = psychology or {}
    consistency = consistency or {}
    behavior = behavior or {}

    score = 0

    # --------------------------
    # Win Rate (150 pts)
    # --------------------------

    win_rate = statistics.get("win_rate", 0)

    score += min(win_rate, 100) * 1.5

    # --------------------------
    # Profit Factor (200 pts)
    # --------------------------

    pf = statistics.get("profit_factor", 0)

    if pf >= 3:
        score += 200
    elif pf >= 2:
        score += 170
    elif pf >= 1.5:
        score += 130
    elif pf >= 1:
        score += 90
    else:
        score += 30

    # --------------------------
    # Recovery Factor (150 pts)
    # --------------------------

    recovery = risk.get("recovery_factor", 0)

    score += min(recovery * 30, 150)

    # --------------------------
    # Drawdown (150 pts)
    # Lower drawdown = higher score
    # --------------------------

    drawdown = risk.get("maximum_drawdown", 0)

    if drawdown <= 2:
        score += 150
    elif drawdown <= 5:
        score += 120
    elif drawdown <= 10:
        score += 80
    elif drawdown <= 20:
        score += 40
    else:
        score += 10

    # --------------------------
    # Expectancy (100 pts)
    # --------------------------

    expectancy = risk.get("expectancy", 0)

    if expectancy > 0:
        score += min(expectancy * 10, 100)

    # --------------------------
    # Psychology
    # --------------------------

    score += psychology.get("score", 0)

    # --------------------------
    # Consistency
    # --------------------------

    score += consistency.get("score", 0)

    # --------------------------
    # Behavior
    # --------------------------

    score += behavior.get("score", 0)

    score = round(min(score, 1000), 2)

    grade = calculate_grade(score)

    return {
        "score": score,
        "grade": grade
    }


def calculate_grade(score):

    if score >= 950:
        return "S+"

    if score >= 900:
        return "S"

    if score >= 850:
        return "A+"

    if score >= 800:
        return "A"

    if score >= 700:
        return "B"

    if score >= 600:
        return "C"

    if score >= 500:
        return "D"

    return "F"