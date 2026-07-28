from services.strategy_score import ScoreComponent


GOOD = {
    "calm",
    "focused",
    "confident",
    "disciplined",
}


def score_psychology(
    strategy,
    payload,
):
    emotion = (
        payload.user_emotion or ""
    ).lower()

    passed = emotion in GOOD

    return ScoreComponent(
        name="Psychology",
        weight=10,
        earned=10 if passed else 3,
        passed=passed,
        explanation=(
            "Trader mindset acceptable."
            if passed
            else "Emotional state may affect execution."
        ),
        matched=[emotion] if passed else [],
        missing=[] if passed else [emotion],
    )
