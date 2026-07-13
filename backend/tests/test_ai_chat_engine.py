import os

from services.ai_chat.engine import generate_chat_reply
from services.ai_chat.memory import clear_history, get_history


def test_ai_chat_reply_uses_context():
    os.environ["OPENAI_API_KEY"] = ""

    user_id = 999
    clear_history(user_id)

    context = {
        "performance": {
            "win_rate": 16.67,
            "profit_factor": 0.32,
        },
        "behavior": {
            "revenge_trading": True,
        },
        "psychology": {
            "discipline_score": 80,
            "confidence_score": 57,
        },
        "consistency": {
            "score": {
                "overall_score": 23,
            }
        },
        "trader_dna": {
            "profile": "Emotional Trader",
        },
    }

    response = generate_chat_reply(
        user_id=user_id,
        message="Why am I losing money?",
        context=context,
    )

    assert "answer" in response
    assert "suggestions" in response
    assert response["answer"]
    assert "16.67" in response["answer"]
    assert "revenge" in response["answer"].lower()

    history = get_history(user_id)

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"

    clear_history(user_id)
