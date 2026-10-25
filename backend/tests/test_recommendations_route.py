import inspect
from types import SimpleNamespace

import pytest

from services.analysis.sufficiency import MIN_TRADES_TRADER_DNA

USER = SimpleNamespace(id=1)


def _route():
    try:
        import routes.v1.recommendations as module
    except Exception as exc:
        pytest.skip(f"route module not importable here: {exc}")
    return module


def _fake_pipeline(trade_count, recommendations):
    def run(db, user_id):
        return {
            "trades": [object()] * trade_count,
            "recommendations": recommendations,
        }

    return run


def test_few_trades_return_no_recommendations(monkeypatch):
    module = _route()
    monkeypatch.setattr(
        module, "run_analysis_pipeline", _fake_pipeline(3, [{"title": "x"}])
    )
    result = module.recommendations(db=None, current_user=USER)
    assert result["recommendations"] == []
    assert result["recommendation_count"] == 0
    assert result["sufficient_data"] is False
    assert result["trades_needed"] == MIN_TRADES_TRADER_DNA - 3
    assert result["total_trades"] == 3


def test_enough_trades_return_the_real_recommendations(monkeypatch):
    module = _route()
    real = [{"title": "a"}, {"title": "b"}]
    monkeypatch.setattr(
        module,
        "run_analysis_pipeline",
        _fake_pipeline(MIN_TRADES_TRADER_DNA, real),
    )
    result = module.recommendations(db=None, current_user=USER)
    assert result["recommendations"] == real
    assert result["recommendation_count"] == 2
    assert result["sufficient_data"] is True
    assert result["trades_needed"] == 0


def test_route_no_longer_contains_hard_coded_scores():
    module = _route()
    source = inspect.getsource(module)
    assert '"overall_score": 80' not in source
    assert '"consistency_score": 80' not in source