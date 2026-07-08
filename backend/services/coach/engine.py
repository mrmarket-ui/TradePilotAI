"""
TradePilot AI Coach Engine

The central orchestrator for all AI modules.
This file does not perform calculations itself.
It coordinates all AI services and returns one
complete response.
"""

from sqlalchemy.orm import Session

from models.trade import Trade

from services.analytics.engine import calculate_statistics

from services.analytics.risk import (
    calculate_max_drawdown,
    calculate_consecutive_wins,
    calculate_consecutive_losses,
    calculate_recovery_factor,
    calculate_expectancy,
    largest_win,
    largest_loss,
    average_holding_hours,
    average_winning_holding_hours,
    average_losing_holding_hours,
    average_risk_reward,
    best_risk_reward,
    worst_risk_reward,
    average_risk,
    average_reward,
)

from services.coach.scoring import calculate_tradepilot_score
from services.coach.serializer import build_ai_response


def build_ai_dashboard(
    db: Session,
    user_id: int,
):
    """
    Builds the complete AI response
    for a single trader.
    """

    trades = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .all()
    )

    # ----------------------------
    # Analytics
    # ----------------------------

    statistics = calculate_statistics(
        db=db,
        user_id=user_id
    )

    # ----------------------------
    # Risk
    # ----------------------------

    risk = {

        "maximum_drawdown":
            calculate_max_drawdown(trades),

        "recovery_factor":
            calculate_recovery_factor(trades),

        "expectancy":
            calculate_expectancy(trades),

        "largest_win":
            largest_win(trades),

        "largest_loss":
            largest_loss(trades),

        "average_holding_hours":
            average_holding_hours(trades),

        "average_winning_holding_hours":
            average_winning_holding_hours(trades),

        "average_losing_holding_hours":
            average_losing_holding_hours(trades),

        "average_risk_reward":
            average_risk_reward(trades),

        "best_risk_reward":
            best_risk_reward(trades),

        "worst_risk_reward":
            worst_risk_reward(trades),

        "average_risk":
            average_risk(trades),

        "average_reward":
            average_reward(trades),

        "longest_win_streak":
            calculate_consecutive_wins(trades),

        "longest_loss_streak":
            calculate_consecutive_losses(trades),
    }

    # ----------------------------
    # Placeholder AI Modules
    # ----------------------------

    psychology = {
        "score": 0
    }

    consistency = {
        "score": 0
    }

    behavior = {
        "score": 0
    }

    strengths = []

    weaknesses = []

    insights = []

    recommendations = []

    # ----------------------------
    # TradePilot Score
    # ----------------------------

    tradepilot_score = calculate_tradepilot_score(
        statistics=statistics,
        risk=risk,
        psychology=psychology,
        consistency=consistency,
        behavior=behavior,
    )

    # ----------------------------
    # Final Response
    # ----------------------------

    return build_ai_response(
        score=tradepilot_score,
        statistics=statistics,
        risk=risk,
        psychology=psychology,
        consistency=consistency,
        behavior=behavior,
        strengths=strengths,
        weaknesses=weaknesses,
        insights=insights,
        recommendations=recommendations,
    )