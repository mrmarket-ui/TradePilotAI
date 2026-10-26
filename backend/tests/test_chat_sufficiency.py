from types import SimpleNamespace

import pytest

from services.ai_chat.sufficiency import apply_data_sufficiency
from services.analysis.sufficiency import MIN_TRADES_TRADER_DNA


def full(trade_count):
    return {
        "risk": {"expectancy": 5},
        "performance": {"win_rate": 60, "profit_factor": 1.8},
        "behavior": {"revenge_trading": True},
        "psychology": {
            "discipline_score": 90,
            "confidence_score": 70,
            "emotional_control": 80,
        },
        "consistency": {"score": {"overall_score": 72}},
        "trader_dna": {
            "profile": "Balanced Trader",
            "strengths": ["x"],
            "weaknesses": ["y"],
        },
        "recommendations": [{"title": "t", "message": "m"}],
        "recent_trades": [{"profit": 10}, {"profit": -5}],
        "trade_count": trade_count,
    }


def test_few_trades_withhold_scores_and_flags():
    result = apply_data_sufficiency(full(3), 3)
    assert set(result) == {
        "trade_count",
        "recent_trades",
        "trader_dna",
        "data_status",
    }
    assert result["recent_trades"] == full(3)["recent_trades"]
    assert result["trader_dna"]["profile"] == "Not enough data yet"
    assert result["data_status"]["trades_logged"] == 3
    assert result["data_status"]["trades_needed"] == MIN_TRADES_TRADER_DNA - 3
    assert "psychology" not in result


def test_zero_trades_need_the_full_minimum():
    result = apply_data_sufficiency({}, 0)
    assert result["data_status"]["trades_needed"] == MIN_TRADES_TRADER_DNA
    assert "recent_trades" not in result


def test_enough_trades_leave_the_context_untouched():
    context = full(MIN_TRADES_TRADER_DNA)
    assert apply_data_sufficiency(context, MIN_TRADES_TRADER_DNA) is context


def _engine():
    try:
        import services.ai_chat.engine as module
    except Exception as exc:
        pytest.skip(f"chat engine not importable here: {exc}")
    return module


def test_fallback_refuses_to_quote_scores_without_data():
    engine = _engine()
    context = apply_data_sufficiency(full(3), 3)
    reply = engine._fallback_reply("How is my psychology?", context)
    assert "don't have enough" in reply
    assert "you have 3" in reply
    assert "discipline score" not in reply.lower()


def test_fallback_declines_profile_questions_without_data():
    engine = _engine()
    context = apply_data_sufficiency(full(3), 3)
    reply = engine._fallback_reply("What is my trader DNA profile?", context)
    assert "don't have enough" in reply


def test_fallback_still_reviews_recent_trades_without_data():
    engine = _engine()
    context = apply_data_sufficiency(full(3), 3)
    reply = engine._fallback_reply("review my recent trades", context)
    assert "I reviewed 2 recent trades" in reply


def test_fallback_is_unchanged_with_enough_data():
    engine = _engine()
    reply = engine._fallback_reply(
        "tell me about my discipline", full(MIN_TRADES_TRADER_DNA)
    )
    assert "Your discipline score is 90" in reply


def _route():
    try:
        import routes.v1.ai_chat as module
    except Exception as exc:
        pytest.skip(f"chat route not importable here: {exc}")
    return module


def _run(module, monkeypatch, trade_count):
    seen = {}
    monkeypatch.setattr(
        module, "build_chat_context", lambda db, user_id: full(trade_count)
    )

    def fake_reply(user_id, message, context):
        seen["context"] = context
        return {"reply": "ok"}

    monkeypatch.setattr(module, "generate_chat_reply", fake_reply)
    module.chat_with_coach(
        payload=SimpleNamespace(message="hi"),
        db=None,
        current_user=SimpleNamespace(id=1),
    )
    return seen["context"]


def test_route_trims_the_context_for_a_new_account(monkeypatch):
    context = _run(_route(), monkeypatch, 3)
    assert "psychology" not in context
    assert context["data_status"]["sufficient_data"] is False


def test_route_keeps_the_full_context_with_enough_trades(monkeypatch):
    count = MIN_TRADES_TRADER_DNA + 2
    context = _run(_route(), monkeypatch, count)
    assert context == full(count)


def test_system_prompt_tells_the_model_not_to_invent_scores():
    from services.ai_chat.prompts import SYSTEM_PROMPT

    assert "data_status" in SYSTEM_PROMPT