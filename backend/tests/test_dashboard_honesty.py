import pytest

from services.analysis.sufficiency import MIN_TRADES_TRADER_DNA
from services.dashboard.intelligence.headline import generate_headline


def test_empty_account_gets_a_baseline_headline_not_a_warning():
    headline = generate_headline(
        {
            "trader_dna": {"profile": "Not enough data yet", "trades_needed": 8},
            "performance": {"profit_factor": 0},
            "behavior": {"revenge_trading": True},
        }
    )
    assert headline["title"] == "Build Your Baseline"
    assert "8" in headline["message"]


def test_enough_data_keeps_normal_headlines():
    headline = generate_headline(
        {
            "trader_dna": {"profile": "Balanced Trader"},
            "performance": {"profit_factor": 0.5},
            "behavior": {},
        }
    )
    assert headline["title"] == "Protect Your Capital"


def _dashboard_module():
    try:
        import services.dashboard.dashboard as module
    except Exception as exc:  # environment without database settings
        pytest.skip(f"dashboard module not importable here: {exc}")
    return module


def _fake_dashboard(total_trades):
    return {
        "summary": {"total_trades": total_trades},
        "overview": {"consistency_score": 14.0, "discipline_score": 100.0},
    }


def test_dashboard_scores_hidden_without_data(monkeypatch):
    module = _dashboard_module()
    monkeypatch.setattr(
        module, "_get_dashboard_full", lambda db, user_id: _fake_dashboard(2)
    )
    result = module.get_dashboard(db=None, user_id=1)
    assert result["overview"]["consistency_score"] is None
    assert result["overview"]["discipline_score"] is None
    assert result["overview"]["sufficient_data"] is False
    assert result["overview"]["trades_needed"] == MIN_TRADES_TRADER_DNA - 2


def test_dashboard_scores_kept_with_enough_data(monkeypatch):
    module = _dashboard_module()
    monkeypatch.setattr(
        module,
        "_get_dashboard_full",
        lambda db, user_id: _fake_dashboard(MIN_TRADES_TRADER_DNA),
    )
    result = module.get_dashboard(db=None, user_id=1)
    assert result["overview"]["consistency_score"] == 14.0