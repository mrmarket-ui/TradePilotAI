from services.analytics.engine import calculate_statistics
from services.analytics.risk import (
    calculate_max_drawdown,
    calculate_expectancy,
    average_risk_reward,
)

from services.ai.behavior import analyze_behavior
from services.ai.psychology import psychology_score
from services.ai.recommendations import generate_recommendations
from services.ai.reports import build_report


def build_ai_coach(db, user_id):

    stats = calculate_statistics(db, user_id)

    trades = (
        db.query(stats["model"])
        .filter(stats["model"].user_id == user_id)
        .all()
    )

    risk = {

        "maximum_drawdown":
            calculate_max_drawdown(trades),

        "expectancy":
            calculate_expectancy(trades),

        "average_risk_reward":
            average_risk_reward(trades)

    }

    behavior = analyze_behavior(trades)

    psychology = psychology_score(trades)

    recommendations = generate_recommendations(
        stats,
        risk
    )

    report = build_report(
        stats,
        risk
    )

    return {

        "statistics": stats,

        "risk": risk,

        "behavior": behavior,

        "psychology": psychology,

        "recommendations": recommendations,

        "report": report

    }
