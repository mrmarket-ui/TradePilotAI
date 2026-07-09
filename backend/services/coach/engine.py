from services.coach.score import calculate_coach_score
from services.coach.strengths import identify_strengths
from services.coach.weaknesses import identify_weaknesses
from services.coach.focus import generate_daily_focus
from services.coach.plan import generate_action_plan


def build_ai_coach(analysis: dict) -> dict:
    """
    Build the complete AI coaching report.
    """

    score = calculate_coach_score(analysis)

    strengths = identify_strengths(analysis)

    weaknesses = identify_weaknesses(analysis)

    focus = generate_daily_focus(
        strengths,
        weaknesses
    )

    plan = generate_action_plan(
        weaknesses
    )

    return {

        "overall_score": score["score"],

        "overall_grade": score["grade"],

        "strengths": strengths,

        "weaknesses": weaknesses,

        "daily_focus": focus,

        "action_plan": plan,

    }
