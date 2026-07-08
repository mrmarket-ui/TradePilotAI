from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user

from models.trade import Trade
from models.user import User

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

router = APIRouter(
    prefix="/risk",
    tags=["Risk Analytics"]
)


@router.get("/")
def risk_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    trades = (
        db.query(Trade)
        .filter(Trade.user_id == current_user.id)
        .all()
    )

    return {
        "maximum_drawdown": calculate_max_drawdown(trades),
        "recovery_factor": calculate_recovery_factor(trades),
        "expectancy": calculate_expectancy(trades),

        "longest_win_streak": calculate_consecutive_wins(trades),
        "longest_loss_streak": calculate_consecutive_losses(trades),

        "largest_win": largest_win(trades),
        "largest_loss": largest_loss(trades),

        "average_holding_hours": average_holding_hours(trades),
        "average_winning_holding_hours": average_winning_holding_hours(trades),
        "average_losing_holding_hours": average_losing_holding_hours(trades),

        "average_risk_reward": average_risk_reward(trades),
        "best_risk_reward": best_risk_reward(trades),
        "worst_risk_reward": worst_risk_reward(trades),

        "average_risk": average_risk(trades),
        "average_reward": average_reward(trades),
    }