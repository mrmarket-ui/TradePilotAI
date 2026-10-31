"""
Behaviour analysis needs real open and close times.

Trades logged by hand without times still count for win rate and profit
factor, but they cannot show revenge trading, holding time or session habits.
Without this gate, ten untimed trades would unlock "Excellent discipline"
simply because nothing bad could be measured.
"""

from datetime import datetime
from types import SimpleNamespace

import pytest

from schemas.analysis.trader_dna import TraderDNAAnalysis
from services.ai_chat.sufficiency import apply_data_sufficiency
from services.analysis.sufficiency import (
    MIN_TRADES_TRADER_DNA,
    insufficient_trader_dna,
    timed_trade_count,
)
from services.trader_dna.engine import analyze_trader_dna

T = datetime(2026, 10, 20, 9, 0)
USER = SimpleNamespace(id=1)


def trade(opened=T, closed=T):
    return SimpleNamespace(opened_at=opened, closed_at=closed)


# ---------------- the counting rule ----------------

def test_a_trade_needs_both_times_to_count():
    trades = [trade(), trade(None, T), trade(T, None), trade(None, None), SimpleNamespace()]
    assert timed_trade_count(trades) == 1


def test_nothing_to_count():
    assert timed_trade_count([]) == 0
    assert timed_trade_count(None) == 0


# ---------------- the locked Trader DNA result ----------------

def test_missing_times_has_its_own_reason_and_count():
    result = insufficient_trader_dna(12, 3)
    assert result["reason"] == "missing_times"
    assert result["trades_needed"] == MIN_TRADES_TRADER_DNA - 3
    assert result["sufficient_data"] is False
    assert result["strengths"] == [] and result["weaknesses"] == []


def test_too_few_trades_keeps_the_original_reason():
    assert insufficient_trader_dna(4, 4)["reason"] == "few_trades"
    assert insufficient_trader_dna(4, 4)["trades_needed"] == MIN_TRADES_TRADER_DNA - 4
    assert insufficient_trader_dna(4)["reason"] == "few_trades"


def test_the_reason_survives_the_api_schema():
    # AnalysisService builds TraderDNAAnalysis(**trader_dna); an unknown field
    # would be dropped silently and the page could never show the right message.
    schema = TraderDNAAnalysis(**insufficient_trader_dna(12, 3))
    assert schema.reason == "missing_times"
    assert schema.trades_needed == MIN_TRADES_TRADER_DNA - 3


# ---------------- the Trader DNA engine ----------------

def _dna(total, timed="omit"):
    kwargs = {}
    if timed != "omit":
        kwargs["timed_trades"] = timed

    return analyze_trader_dna(
        statistics={"total_trades": total, "win_rate": 65.0},
        risk={"risk_score": 85},
        consistency={"score": 85},
        psychology={
            "discipline_score": 90,
            "emotional_control": 90,
            "stress_score": 10,
            "fear_score": 10,
            "greed_score": 10,
        },
        behavior={
            "position_size_discipline": True,
            "strategy_discipline": True,
            "session_discipline": True,
        },
        **kwargs,
    )


def test_enough_trades_without_times_do_not_unlock_trader_dna():
    result = _dna(MIN_TRADES_TRADER_DNA + 5, 2)
    assert result["profile"] == "Not enough data yet"
    assert result["reason"] == "missing_times"
    assert result["strengths"] == []


def test_enough_timed_trades_unlock_it():
    result = _dna(MIN_TRADES_TRADER_DNA, MIN_TRADES_TRADER_DNA)
    assert result["profile"] != "Not enough data yet"
    assert "Excellent discipline" in result["strengths"]


def test_callers_that_pass_no_timed_count_behave_as_before():
    assert _dna(MIN_TRADES_TRADER_DNA)["profile"] != "Not enough data yet"
    assert _dna(3)["reason"] == "few_trades"


# ---------------- the pipeline passes the count ----------------

def _pipeline(monkeypatch, trades):
    try:
        import services.analysis.pipeline as module
    except Exception as exc:
        pytest.skip(f"pipeline not importable here: {exc}")

    monkeypatch.setattr(module, "load_user_trades", lambda db, user_id: trades)
    monkeypatch.setattr(
        module,
        "calculate_statistics_from_trades",
        lambda t: {"total_trades": len(t), "win_rate": 60.0, "profit_factor": 1.5},
    )
    monkeypatch.setattr(module, "build_risk_summary", lambda t: {"risk_score": 80, "recovery_factor": 2})
    monkeypatch.setattr(module, "analyze_behavior", lambda t: {})
    monkeypatch.setattr(
        module,
        "analyze_psychology",
        lambda trades, behavior: {
            "discipline_score": 90,
            "emotional_control": 90,
            "stress_score": 10,
            "fear_score": 10,
            "greed_score": 10,
        },
    )
    monkeypatch.setattr(module, "analyze_consistency", lambda **kwargs: {"score": {"overall_score": 70}})
    monkeypatch.setattr(module, "generate_recommendations", lambda **kwargs: [])

    return module.run_analysis_pipeline(db=None, user_id=1)


def test_pipeline_locks_trader_dna_for_untimed_trades(monkeypatch):
    result = _pipeline(monkeypatch, [trade(None, None) for _ in range(MIN_TRADES_TRADER_DNA + 2)])
    assert result["trader_dna"]["sufficient_data"] is False
    assert result["trader_dna"]["reason"] == "missing_times"
    assert result["trader_dna"]["trades_needed"] == MIN_TRADES_TRADER_DNA


def test_pipeline_unlocks_trader_dna_for_timed_trades(monkeypatch):
    result = _pipeline(monkeypatch, [trade() for _ in range(MIN_TRADES_TRADER_DNA)])
    assert result["trader_dna"]["profile"] != "Not enough data yet"


# ---------------- the dashboard ----------------

def _dashboard():
    try:
        import services.dashboard.dashboard as module
    except Exception as exc:
        pytest.skip(f"dashboard module not importable here: {exc}")
    return module


def _locked_dashboard(total, needed, reason="missing_times"):
    return {
        "summary": {"total_trades": total},
        "overview": {"consistency_score": 70.0, "discipline_score": 90.0},
        "trader_dna": {"sufficient_data": False, "trades_needed": needed, "reason": reason},
        "recommendations": [{"title": "Improve Consistency"}],
    }


def test_dashboard_locks_behaviour_scores_when_times_are_missing(monkeypatch):
    module = _dashboard()
    monkeypatch.setattr(module, "_get_dashboard_full", lambda db, user_id: _locked_dashboard(15, 7))
    result = module.get_dashboard(db=None, user_id=1)
    assert result["overview"]["consistency_score"] is None
    assert result["overview"]["discipline_score"] is None
    assert result["overview"]["trades_needed"] == 7
    card = result["recommendations"][0]
    assert card["title"] == "Add open and close times"
    assert "7" in card["message"]
    assert len(result["recommendations"]) == 1


def test_dashboard_keeps_everything_when_behaviour_is_unlocked(monkeypatch):
    module = _dashboard()
    full = {
        "summary": {"total_trades": 15},
        "overview": {"consistency_score": 70.0, "discipline_score": 90.0},
        "trader_dna": {"sufficient_data": True},
        "recommendations": [{"title": "Improve Consistency"}],
    }
    monkeypatch.setattr(module, "_get_dashboard_full", lambda db, user_id: full)
    result = module.get_dashboard(db=None, user_id=1)
    assert result["overview"]["consistency_score"] == 70.0
    assert result["recommendations"] == [{"title": "Improve Consistency"}]


# ---------------- recommendations route ----------------

def test_recommendations_are_withheld_when_times_are_missing(monkeypatch):
    try:
        import routes.v1.recommendations as module
    except Exception as exc:
        pytest.skip(f"route not importable here: {exc}")

    monkeypatch.setattr(
        module,
        "run_analysis_pipeline",
        lambda db, user_id: {
            "trades": [object()] * 15,
            "recommendations": [{"title": "x"}],
            "trader_dna": {"sufficient_data": False, "trades_needed": 6, "reason": "missing_times"},
        },
    )
    result = module.recommendations(db=None, current_user=USER)
    assert result["recommendations"] == []
    assert result["sufficient_data"] is False
    assert result["trades_needed"] == 6
    assert result["reason"] == "missing_times"


# ---------------- AI chat ----------------

CHAT_CONTEXT = {
    "psychology": {"discipline_score": 90},
    "recent_trades": [{"profit": 10}, {"profit": -5}],
    "trader_dna": {"sufficient_data": False, "trades_needed": 6, "reason": "missing_times"},
}


def test_chat_context_is_trimmed_when_times_are_missing():
    result = apply_data_sufficiency(dict(CHAT_CONTEXT), 15)
    assert "psychology" not in result
    assert result["data_status"]["reason"] == "missing_times"
    assert result["data_status"]["trades_needed"] == 6
    assert result["recent_trades"] == CHAT_CONTEXT["recent_trades"]


def test_chat_context_is_untouched_when_behaviour_is_unlocked():
    context = {"psychology": {"discipline_score": 90}, "trader_dna": {"sufficient_data": True}}
    assert apply_data_sufficiency(context, 15) is context


def test_chat_fallback_asks_for_times_not_more_trades():
    try:
        import services.ai_chat.engine as engine
    except Exception as exc:
        pytest.skip(f"chat engine not importable here: {exc}")

    trimmed = apply_data_sufficiency(dict(CHAT_CONTEXT), 15)
    reply = engine._fallback_reply("How is my psychology?", trimmed)
    assert "open and close times" in reply
    assert "6 more trades" in reply
    assert "discipline score" not in reply.lower()