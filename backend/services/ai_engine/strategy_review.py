import json

from google.genai import types, errors

from services.ai_engine.strategy_signal import (
    AI_PROVIDER,
    GEMINI_MODEL,
    OPENAI_MODEL,
    clean_json,
    get_gemini_client,
    get_openai_client,
    strategy_context,
)


def build_strategy_review_prompt(
    strategy,
) -> str:
    context = strategy_context(
        strategy
    )

    extra_context = {
        "description":
            strategy.description,

        "strategy_type":
            strategy.strategy_type,

        "preferred_direction":
            strategy.preferred_direction,

        "allowed_weekdays":
            strategy.allowed_weekdays,

        "psychology_rules":
            strategy.psychology_rules,

        "pre_trade_checklist":
            strategy.pre_trade_checklist,

        "post_trade_checklist":
            strategy.post_trade_checklist,

        "max_daily_loss_percent":
            strategy.max_daily_loss_percent,

        "max_weekly_loss_percent":
            strategy.max_weekly_loss_percent,

        "max_open_positions":
            strategy.max_open_positions,

        "avoid_high_impact_news":
            strategy.avoid_high_impact_news,

        "news_minutes_before":
            strategy.news_minutes_before,

        "news_minutes_after":
            strategy.news_minutes_after,

        "requires_user_approval":
            strategy.requires_user_approval,
    }

    full_context = {
        **context,
        **extra_context,
    }

    return f"""
You are TradePilot AI's Strategy Review Engine.

Review the trading strategy supplied below.

Your task is to evaluate the STRUCTURE,
CLARITY, RISK CONTROLS and COMPLETENESS
of the trading plan.

Do NOT predict profitability.

Do NOT claim that the strategy will make
money.

Do NOT invent historical performance,
win rate, expectancy or backtest results.

Do NOT judge the strategy using information
that is not supplied.

A high score means the strategy is clearly
defined and disciplined. It does NOT mean
the strategy is profitable.

USER STRATEGY:

{json.dumps(
    full_context,
    indent=2,
)}

Return valid JSON only using this structure:

{{
  "health_score": 0,
  "grade": "",
  "strengths": [],
  "weaknesses": [],
  "missing_elements": [],
  "risk_assessment": "",
  "priority_improvements": [],
  "summary": ""
}}

SCORING GUIDANCE:

90-100:
Highly structured and comprehensive.

75-89:
Strong structure with minor weaknesses.

60-74:
Usable but important areas need improvement.

40-59:
Incomplete or weakly defined.

0-39:
Major strategy-definition gaps.

IMPORTANT:

health_score must be between 0 and 100.

grade must be one of:

"Excellent"
"Strong"
"Developing"
"Weak"
"Incomplete"

strengths should contain specific strengths
found in the supplied strategy.

weaknesses should identify unclear,
contradictory or underdeveloped areas.

missing_elements should contain important
strategy components that are absent.

priority_improvements should contain at most
5 practical improvements ordered from most
important to least important.

risk_assessment should discuss the quality
of the strategy's risk controls, not market
risk predictions.

summary should be concise and educational.

Never provide guaranteed-trade language.

Never invent evidence.
"""


def review_strategy_openai(
    strategy,
) -> dict:
    client = get_openai_client()

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type":
                            "input_text",
                        "text":
                            build_strategy_review_prompt(
                                strategy
                            ),
                    },
                ],
            },
        ],
    )

    return clean_json(
        response.output_text
    )


def review_strategy_gemini(
    strategy,
) -> dict:
    client = get_gemini_client()

    models_to_try = [
        GEMINI_MODEL,
        "gemini-3.6-flash",
    ]

    last_error = None

    for model_name in models_to_try:
        try:
            response = (
                client.models.generate_content(
                    model=model_name,
                    contents=[
                        build_strategy_review_prompt(
                            strategy
                        ),
                    ],
                    config=
                        types.GenerateContentConfig(
                            response_mime_type=
                                "application/json",

                            temperature=0.1,
                        ),
                )
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned no strategy review."
                )

            return clean_json(
                response.text
            )

        except errors.ServerError as exc:
            last_error = exc

            code = getattr(
                exc,
                "code",
                None,
            )

            if code in {
                503,
                504,
            }:
                continue

            raise RuntimeError(
                "Gemini service is temporarily unavailable."
            ) from exc

        except Exception as exc:
            last_error = exc

            message = str(exc)

            if (
                "429" in message
                or "RESOURCE_EXHAUSTED" in message
                or "503" in message
                or "504" in message
                or "UNAVAILABLE" in message
                or "DEADLINE_EXCEEDED" in message
            ):
                continue

            raise

    last_message = str(
        last_error or ""
    )

    if (
        "429" in last_message
        or "RESOURCE_EXHAUSTED" in last_message
    ):
        raise RuntimeError(
            "AI service quota reached. "
            "Please try again later."
        ) from last_error

    raise RuntimeError(
        "AI review service is busy. "
        "Please try again shortly."
    ) from last_error


def normalize_strategy_review(
    result: dict,
) -> dict:
    try:
        score = float(
            result.get(
                "health_score",
                0,
            )
            or 0
        )

    except (
        TypeError,
        ValueError,
    ):
        score = 0

    score = min(
        100,
        max(
            0,
            score,
        ),
    )

    result[
        "health_score"
    ] = round(
        score,
        1,
    )


    allowed_grades = {
        "Excellent",
        "Strong",
        "Developing",
        "Weak",
        "Incomplete",
    }

    grade = str(
        result.get(
            "grade",
            "",
        )
    ).strip()

    if grade not in allowed_grades:
        if score >= 90:
            grade = "Excellent"

        elif score >= 75:
            grade = "Strong"

        elif score >= 60:
            grade = "Developing"

        elif score >= 40:
            grade = "Weak"

        else:
            grade = "Incomplete"

    result["grade"] = grade


    for key in (
        "strengths",
        "weaknesses",
        "missing_elements",
        "priority_improvements",
    ):
        value = result.get(
            key,
            [],
        )

        if not isinstance(
            value,
            list,
        ):
            value = []

        result[key] = [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]


    result[
        "priority_improvements"
    ] = result[
        "priority_improvements"
    ][:5]


    result[
        "risk_assessment"
    ] = str(
        result.get(
            "risk_assessment",
            "",
        )
        or ""
    ).strip()


    result[
        "summary"
    ] = str(
        result.get(
            "summary",
            "",
        )
        or ""
    ).strip()


    return result


def review_strategy(
    strategy,
) -> dict:
    if AI_PROVIDER == "gemini":
        result = (
            review_strategy_gemini(
                strategy
            )
        )

    elif AI_PROVIDER == "openai":
        result = (
            review_strategy_openai(
                strategy
            )
        )

    else:
        raise RuntimeError(
            f"Unsupported AI_PROVIDER: {AI_PROVIDER}"
        )

    return normalize_strategy_review(
        result
    )
