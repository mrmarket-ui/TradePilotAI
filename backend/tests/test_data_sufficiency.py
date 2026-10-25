from schemas.monthly_review.review import MonthlyReviewResponse
from schemas.weekly_review.review import WeeklyReviewResponse
from services.analysis.sufficiency import (
    MIN_TRADES_REVIEW,
    MIN_TRADES_TRADER_DNA,
    apply_review_gate,
)
from services.trader_dna.engine import analyze_trader_dna


def _weekly(total_trades: int) -> dict:
    return {
        "period_start": "2026-10-18",
        "period_end": "2026-10-25",
        "grade": "F",
        "score": 10.0,
        "summary": "Original summary",
        "metrics": {"total_trades": total_trades},
        "strengths": ["Excellent discipline"],
        "weaknesses": ["Revenge trading"],
        "recommendations": [{"title": "x"}],
        "next_week_mission": "Original mission",
    }


def _monthly(total_trades: int) -> dict:
    return {
        "period_start": "2026-10-01",
        "period_end": "2026-10-25",
        "grade": "F",
        "score": 10.0,
        "summary": "Original summary",
        "metrics": {"total_trades": total_trades},
        "trader_profile": "Balanced Trader",
        "strengths": ["Excellent discipline"],
        "weaknesses": ["Revenge trading"],
        "recommendations": [{"title": "x"}],
        "next_month_mission": "Original mission",
    }


def test_zero_trade_week_has_no_grade():
    gated = apply_review_gate(_weekly(0), "week")
    response = WeeklyReviewResponse(**gated)
    assert response.grade is None
    assert response.score is None
    assert response.strengths == []
    assert response.sufficient_data is False
    assert response.trades_needed == MIN_TRADES_REVIEW


def test_two_trade_week_has_no_grade():
    gated = apply_review_gate(_weekly(2), "week")
    response = WeeklyReviewResponse(**gated)
    assert response.grade is None
    assert response.trades_needed == MIN_TRADES_REVIEW - 2


def test_enough_trades_keeps_the_grade():
    gated = apply_review_gate(_weekly(MIN_TRADES_REVIEW), "week")
    response = WeeklyReviewResponse(**gated)
    assert response.grade == "F"
    assert response.strengths == ["Excellent discipline"]
    assert response.sufficient_data is True


def test_monthly_review_without_data_has_no_grade():
    gated = apply_review_gate(_monthly(1), "month")
    response = MonthlyReviewResponse(**gated)
    assert response.grade is None
    assert response.score is None
    assert "Log at least" in response.next_month_mission


def test_review_without_total_trades_is_left_alone():
    review = _weekly(0)
    review["metrics"] = {}
    assert apply_review_gate(review, "week")["grade"] == "F"


def _dna(total_trades: int, strong: bool = True) -> dict:
    return analyze_trader_dna(
        statistics={"total_trades": total_trades, "win_rate": 65.0 if strong else 10.0},
        risk={"risk_score": 85 if strong else 10},
        consistency={"score": 85 if strong else 10},
        psychology={
            "discipline_score": 90 if strong else 10,
            "emotional_control": 90 if strong else 10,
            "stress_score": 10,
            "fear_score": 10,
            "greed_score": 10,
        },
        behavior={
            "position_size_discipline": strong,
            "strategy_discipline": strong,
            "session_discipline": strong,
        },
    )


def test_two_trades_gives_no_trader_dna():
    result = _dna(2)
    assert result["profile"] == "Not enough data yet"
    assert result["strengths"] == []
    assert result["weaknesses"] == []
    assert result["sufficient_data"] is False
    assert result["trades_needed"] == MIN_TRADES_TRADER_DNA - 2


def test_enough_trades_still_produces_strengths():
    result = _dna(MIN_TRADES_TRADER_DNA)
    assert result["profile"] != "Not enough data yet"
    assert "Excellent discipline" in result["strengths"]


def test_no_invented_fallback_strength():
    result = _dna(MIN_TRADES_TRADER_DNA, strong=False)
    assert "Shows commitment to improving" not in result["strengths"]