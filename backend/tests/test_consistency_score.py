from datetime import datetime

import pytest

from services.analysis.sufficiency import MIN_TRADES_TRADER_DNA
from services.consistency.score import (
    WEIGHTS,
    calculate_consistency_score,
    get_grade,
)


def score(statistics=None, risk=None, psychology=None, improvement="Improving", trade_count=50):
    return calculate_consistency_score(
        statistics=statistics if statistics is not None else {},
        risk=risk if risk is not None else {},
        psychology=psychology if psychology is not None else {},
        behavior={},
        improvement=improvement,
        trade_count=trade_count,
    )


FULL = dict(
    statistics={"win_rate": 50, "profit_factor": 1.0},
    risk={"recovery_factor": 2.0},
    psychology={"discipline_score": 80, "emotional_control": 60},
)


def test_weights_add_up_to_100():
    assert sum(WEIGHTS.values()) == 100


def test_too_few_trades_gives_no_score():
    result = score(**FULL, trade_count=3)
    assert result["sufficient_data"] is False
    assert result["overall_score"] == 0.0
    assert result["grade"] is None
    assert result["breakdown"] == {}
    assert result["trades_needed"] == MIN_TRADES_TRADER_DNA - 3


def test_the_minimum_number_of_trades_unlocks_the_score():
    assert score(**FULL, trade_count=MIN_TRADES_TRADER_DNA - 1)["sufficient_data"] is False
    assert score(**FULL, trade_count=MIN_TRADES_TRADER_DNA)["sufficient_data"] is True


def test_no_trade_count_means_no_gate():
    assert score(**FULL, trade_count=None)["sufficient_data"] is True


def test_hand_checked_score_with_every_component():
    # 80*25 + 60*15 + 50*20 + 50*15 + 40*15 + 100*10 = 6250 -> 62.5
    result = score(**FULL, improvement="Improving")
    assert result["overall_score"] == 62.5
    assert result["grade"] == "C"
    assert result["breakdown"] == {
        "discipline": 80,
        "emotional_control": 60,
        "profitability": 50,
        "win_rate": 50,
        "risk_recovery": 40,
        "improvement": 100,
    }


def test_without_a_trend_the_other_weights_are_rescaled():
    # (80*25 + 60*15 + 50*20 + 50*15 + 40*15) / 90 = 5250 / 90 = 58.33
    result = score(**FULL, improvement="Insufficient Data")
    assert result["overall_score"] == 58.33
    assert "improvement" not in result["breakdown"]
    assert result["weights_used"]["discipline"] == 25
    assert sum(result["weights_used"].values()) == 90


def test_missing_inputs_are_left_out_not_invented():
    # win rate 50*15 + profit factor 1.0 -> 50*20 + Mixed trend 60*10 = 2350 / 45
    result = score(
        statistics={"win_rate": 50, "profit_factor": 1.0},
        improvement="Mixed",
    )
    assert result["overall_score"] == 52.22
    assert set(result["breakdown"]) == {"win_rate", "profitability", "improvement"}


def test_values_are_clamped_to_the_0_100_range():
    best = score(
        statistics={"win_rate": 150, "profit_factor": 5},
        risk={"recovery_factor": 10},
        psychology={"discipline_score": 150, "emotional_control": 100},
        improvement="Improving",
    )
    assert best["overall_score"] == 100.0
    assert best["grade"] == "A+"

    worst = score(
        statistics={"win_rate": -20, "profit_factor": -1},
        risk={"recovery_factor": -3},
        psychology={"discipline_score": -5, "emotional_control": 0},
        improvement="Declining",
    )
    # only the Declining trend (20 * 10 / 100) contributes
    assert worst["overall_score"] == 2.0
    assert worst["grade"] == "F"


def test_win_rate_is_counted_once():
    result = score(**FULL)
    assert [name for name in result["breakdown"] if "win" in name] == ["win_rate"]
    assert not {"psychology", "behavior", "consistency"} & set(result["breakdown"])


def test_legacy_score_keys_no_longer_change_the_result():
    legacy = dict(FULL["psychology"], score=88)
    with_legacy = calculate_consistency_score(
        FULL["statistics"], FULL["risk"], legacy, {"score": 91}, "Improving", 50
    )
    without = score(**FULL)
    assert with_legacy["overall_score"] == without["overall_score"]


def test_unusable_numbers_are_ignored():
    result = score(
        statistics={"win_rate": 50, "profit_factor": float("nan")},
        psychology={"discipline_score": "abc", "emotional_control": None},
        improvement="Insufficient Data",
    )
    assert set(result["breakdown"]) == {"win_rate"}
    assert result["overall_score"] == 50.0


def test_nothing_usable_returns_the_no_data_shape():
    result = score(improvement="Insufficient Data")
    assert result["sufficient_data"] is False
    assert result["overall_score"] == 0.0


@pytest.mark.parametrize(
    "value, grade",
    [(95, "A+"), (85, "A"), (75, "B"), (65, "C"), (55, "D"), (10, "F")],
)
def test_grade_bands(value, grade):
    assert get_grade(value) == grade


# ---------------- the engine passes the trade count through ----------------

class Trade:
    def __init__(self, pair, strategy, profit, day, hour, month):
        self.pair = pair
        self.strategy = strategy
        self.profit = profit
        self.opened_at = datetime(2026, month, day, hour, 0)
        self.closed_at = datetime(2026, month, day, hour + 1, 0)


def _trades(count):
    return [
        Trade("EURUSD", "SMC", 50 if i % 3 else -30, 1 + i % 20, 9 + i % 6, 1 + i % 3)
        for i in range(count)
    ]


def _run_engine(count):
    try:
        from services.consistency.engine import analyze_consistency
    except Exception as exc:
        pytest.skip(f"consistency engine not importable here: {exc}")

    return analyze_consistency(
        _trades(count),
        {"win_rate": 66.0, "profit_factor": 1.8},
        {"recovery_factor": 2.5},
        {"discipline_score": 85, "emotional_control": 90},
        {},
    )


def test_engine_marks_a_small_history_as_insufficient():
    result = _run_engine(4)
    assert result["score"]["sufficient_data"] is False
    assert result["score"]["trades_needed"] == MIN_TRADES_TRADER_DNA - 4


def test_engine_scores_a_real_history():
    result = _run_engine(12)
    assert result["score"]["sufficient_data"] is True
    assert 0 <= result["score"]["overall_score"] <= 100
    assert result["score"]["grade"] is not None