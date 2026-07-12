from services.ai_chat.prompts import FOLLOW_UPS


def build_response(answer: str):
    return {
        "answer": answer,
        "suggestions": FOLLOW_UPS[:3],
    }
