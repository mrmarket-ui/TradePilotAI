"""
Real tests for the behaviour detectors and the psychology scores.

Each test uses a small hand-checked fixture and asserts the rule that the
function documents. The older print-style test files did not assert anything.
"""

from datetime import datetime, timedelta

from services.behavior.fomo import detect_fomo
from services.behavior.holding import analyze_holding_behavior
from services.behavior.revenge import detect_revenge_trading
from services.behavior.weekend import detect_weekend_trading
from services.psychology.confidence import calculate_confidence_score
from services.psychology.discipline import calculate_discipline_score
from services.psychology.emotion import calculate_emotional_scores
from services.psychology.stress import calculate_stress_score

MONDAY = datetime(2026, 10, 5, 9, 0)
SATURDAY = datetime(2026, 10, 10, 9, 0)


class T:
    """Minimal stand-in for a Trade row."""

    def __init__(
        self,
        profit=0.0,
        opened_at=None,
        closed_at=None,
        entry=None,
        stop_loss=None,
        take_profit=None,
    ):
        self.profit = profit
        self.opened_at = opened_at
        self.closed_at = closed_at
        self.entry = entry
        self.stop_loss = stop_loss
        self.take_profit = take_profit


def trade(profit, open_offset_min, hold_min):
    opened = MONDAY + timedelta(minutes=open_offset_min)
    return T(profit, opened, opened + timedelta(minutes=hold_min))


def levels(entry, stop, target):
    return T(0, None, None, entry, stop, target)


def poor():
    return levels(1.1000, 1.0950, 1.1020)  # reward is 0.4 of the risk


def good():
    return levels(1.1000, 1.0950, 1.1100)  # reward is 2 times the risk


# ---------------- revenge trading ----------------

def test_quick_reentry_after_a_loss_is_flagged():
    loser = trade(-50, 0, 60)  # closes 10:00
    nxt = trade(20, 80, 30)  # opens 10:20
    assert detect_revenge_trading([loser, nxt]) is True


def test_reentry_exactly_at_the_cooldown_is_flagged():
    loser = trade(-50, 0, 60)  # closes 10:00
    nxt = trade(20, 90, 30)  # opens 10:30
    assert detect_revenge_trading([loser, nxt]) is True


def test_reentry_after_the_cooldown_is_not_flagged():
    loser = trade(-50, 0, 60)  # closes 10:00
    nxt = trade(20, 121, 30)  # opens 11:01
    assert detect_revenge_trading([loser, nxt]) is False


def test_quick_trade_after_a_win_is_not_revenge():
    winner = trade(50, 0, 60)
    nxt = trade(20, 70, 30)
    assert detect_revenge_trading([winner, nxt]) is False


def test_no_trades_means_no_revenge_flag():
    assert detect_revenge_trading([]) is False


# ---------------- holding behaviour ----------------

def test_holding_losers_longer_than_winners_is_flagged():
    result = analyze_holding_behavior([trade(100, 0, 60), trade(-100, 200, 180)])
    assert result["holding_losers_too_long"] is True
    assert result["cutting_winners_too_early"] is True


def test_similar_holding_times_are_not_flagged():
    result = analyze_holding_behavior([trade(100, 0, 120), trade(-100, 200, 120)])
    assert result["holding_losers_too_long"] is False
    assert result["cutting_winners_too_early"] is False


def test_holding_needs_both_winners_and_losers():
    result = analyze_holding_behavior([trade(100, 0, 60), trade(50, 100, 60)])
    assert result == {
        "holding_losers_too_long": False,
        "cutting_winners_too_early": False,
    }


# ---------------- weekend trading ----------------

def test_weekend_trade_is_detected():
    assert detect_weekend_trading([T(1, SATURDAY), T(1, MONDAY)]) is True


def test_weekday_only_trading_is_not_flagged():
    assert detect_weekend_trading([T(1, MONDAY), T(1, MONDAY + timedelta(days=1))]) is False


def test_trades_without_an_open_time_are_ignored():
    assert detect_weekend_trading([T(1, None)]) is False


# ---------------- FOMO (poor reward-to-risk entries) ----------------

def test_fomo_needs_more_than_40_percent_poor_reward_to_risk():
    assert detect_fomo([poor(), poor(), poor(), good(), good()]) is True  # 60%
    assert detect_fomo([poor(), poor(), good(), good(), good()]) is False  # exactly 40%
    assert detect_fomo([good(), good()]) is False


def test_fomo_ignores_trades_without_usable_levels():
    assert detect_fomo([T(0), levels(1.1, None, 1.2), levels(1.1, 1.1, 1.2)]) is False


# ---------------- discipline score ----------------

def test_discipline_starts_at_100_without_bad_habits():
    assert calculate_discipline_score({}) == 100


def test_discipline_deducts_per_habit():
    assert calculate_discipline_score({"revenge_trading": True}) == 80
    assert calculate_discipline_score({"revenge_trading": True, "fomo_detected": True}) == 65
    assert calculate_discipline_score({"position_size_discipline": False}) == 85


def test_discipline_never_goes_below_zero():
    worst = {
        "revenge_trading": True,
        "fomo_detected": True,
        "holding_losers_too_long": True,
        "cutting_winners_too_early": True,
        "weekend_trading": True,
        "position_size_discipline": False,
        "strategy_discipline": False,
        "session_discipline": False,
    }
    assert calculate_discipline_score(worst) == 0


# ---------------- emotional scores ----------------

def test_emotional_scores_start_neutral():
    assert calculate_emotional_scores({}) == {
        "greed_score": 0,
        "fear_score": 0,
        "emotional_control": 100,
    }


def test_revenge_and_fomo_raise_greed_and_lower_control():
    result = calculate_emotional_scores({"revenge_trading": True, "fomo_detected": True})
    assert result == {"greed_score": 45, "fear_score": 0, "emotional_control": 65}


def test_fear_comes_from_cutting_winners_and_holding_losers():
    result = calculate_emotional_scores(
        {"cutting_winners_too_early": True, "holding_losers_too_long": True}
    )
    assert result["fear_score"] == 40
    assert result["emotional_control"] == 85


# ---------------- stress score ----------------

def test_stress_adds_up_from_behaviour():
    assert calculate_stress_score({}) == 0
    assert calculate_stress_score({"revenge_trading": True}) == 30
    assert calculate_stress_score(
        {
            "revenge_trading": True,
            "fomo_detected": True,
            "holding_losers_too_long": True,
            "weekend_trading": True,
        }
    ) == 80


# ---------------- confidence score ----------------

def test_confidence_with_no_trades_is_neutral():
    assert calculate_confidence_score([]) == 50


def test_confidence_follows_win_rate():
    trades = [T(100), T(100), T(100), T(-50)]
    assert calculate_confidence_score(trades) == 80  # 50 + 0.75 * 40


def test_confidence_trend_adjustment_and_limits():
    trades = [T(100), T(100), T(100), T(-50)]
    assert calculate_confidence_score(trades, "improving") == 90
    assert calculate_confidence_score(trades, "declining") == 70
    assert calculate_confidence_score([T(100)], "improving") == 100
    assert calculate_confidence_score([T(-100)], "declining") == 40