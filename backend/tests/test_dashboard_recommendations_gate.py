import pytest

from services.analysis.sufficiency import MIN_TRADES_TRADER_DNA


def _module():
    try:
        import services.dashboard.dashboard as module
    except Exception as exc:
        pytest.skip(f"dashboard module not importable here: {exc}")
    return module


def _fake(total_trades):
    return {
        "summary": {"total_trades": total_trades},
        "overview": {"consistency_score": 14.0, "discipline_score": 100.0},
        "recommendations": [{"title": "Improve Consistency"}],
    }


def test_few_trades_replace_generic_advice_with_one_honest_card(monkeypatch):
    module = _module()
    monkeypatch.setattr(module, "_get_dashboard_full", lambda db, user_id: _fake(2))
    result = module.get_dashboard(db=None, user_id=1)
    assert len(result["recommendations"]) == 1
    card = result["recommendations"][0]
    assert card["title"] == "Log more trades"
    assert str(MIN_TRADES_TRADER_DNA - 2) in card["message"]
    assert set(card) == {"priority", "category", "title", "message"}


def test_enough_trades_keep_the_real_recommendations(monkeypatch):
    module = _module()
    monkeypatch.setattr(
        module,
        "_get_dashboard_full",
        lambda db, user_id: _fake(MIN_TRADES_TRADER_DNA),
    )
    result = module.get_dashboard(db=None, user_id=1)
    assert result["recommendations"] == [{"title": "Improve Consistency"}]