import json

from google.genai import (
    errors,
    types,
)

from services.ai_engine.strategy_signal import (
    AI_PROVIDER,
    GEMINI_MODEL,
    OPENAI_MODEL,
    clean_json,
    get_gemini_client,
    get_openai_client,
    strategy_context,
)


ALLOWED_FIELDS = {
    "markets",
    "sessions",
    "timeframes",
    "entry_rules",
    "exit_rules",
    "confirmations",
    "psychology_rules",
    "trade_management_rules",
    "max_risk_percent",
    "max_daily_loss_percent",
    "max_weekly_loss_percent",
    "max_trades_per_day",
    "max_consecutive_losses",
}


def build_improvement_prompt(
    strategy,
) -> str:
    context = strategy_context(
        strategy
    )

    context.update(
        {
            "description":
                strategy.description,

            "strategy_type":
                getattr(
                    strategy,
                    "strategy_type",
                    None,
                ),

            "psychology_rules":
                strategy.psychology_rules,

            "max_daily_loss_percent":
                strategy.max_daily_loss_percent,

            "max_weekly_loss_percent":
                strategy.max_weekly_loss_percent,

            "requires_user_approval":
                strategy.requires_user_approval,
        }
    )

    return f"""
You are TradePilot AI's strategy improvement engine.

Review this trading strategy and propose practical
improvements.

IMPORTANT:

Do NOT execute trades.

Do NOT promise profit.

Do NOT silently change the user's strategy.

Every suggestion must be presented for user approval.

Only suggest changes to these editable fields:

markets
sessions
timeframes
entry_rules
exit_rules
confirmations
psychology_rules
trade_management_rules
max_risk_percent
max_daily_loss_percent
max_weekly_loss_percent
max_trades_per_day
max_consecutive_losses

For list fields, use action "append" unless an existing
rule genuinely needs replacement.

For numeric settings, use action "set".

Avoid duplicate suggestions.

Keep suggestions specific and usable.

STRATEGY:

{json.dumps(context)}

Return VALID JSON ONLY:

{{
  "current_score": 0,
  "projected_score": 0,
  "summary": "",
  "suggestions": [
    {{
      "id": "unique_short_id",
      "category": "risk | entry | exit | confirmation | psychology | management | market | schedule",
      "title": "",
      "reason": "",
      "field": "",
      "action": "append | set",
      "value": "",
      "projected_impact": 0
    }}
  ]
}}

Rules:

current_score must be 0-100.

projected_score must be 0-100.

projected_score must not be lower than current_score.

projected_impact must be 0-25.

Return no more than 8 suggestions.

For list-field suggestions, value must be a string
containing one complete proposed rule.

For numeric fields, value must be a number.

Never invent performance evidence.
"""


def improve_strategy_openai(
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
                            build_improvement_prompt(
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


def improve_strategy_gemini(
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
                        build_improvement_prompt(
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
                    "Gemini returned no strategy improvements."
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
        "AI improvement service is busy. "
        "Please try again shortly."
    ) from last_error


def normalize_improvements(
    result: dict,
) -> dict:
    def score_value(
        key: str,
    ) -> float:
        try:
            value = float(
                result.get(
                    key,
                    0,
                )
                or 0
            )

        except (
            TypeError,
            ValueError,
        ):
            value = 0

        return round(
            min(
                100,
                max(
                    0,
                    value,
                ),
            ),
            1,
        )

    current_score = score_value(
        "current_score"
    )

    projected_score = score_value(
        "projected_score"
    )

    projected_score = max(
        current_score,
        projected_score,
    )

    suggestions = result.get(
        "suggestions",
        [],
    )

    if not isinstance(
        suggestions,
        list,
    ):
        suggestions = []

    normalized = []

    for index, item in enumerate(
        suggestions[:8],
        start=1,
    ):
        if not isinstance(
            item,
            dict,
        ):
            continue

        field = str(
            item.get(
                "field",
                "",
            )
        ).strip()

        if field not in ALLOWED_FIELDS:
            continue

        action = str(
            item.get(
                "action",
                "append",
            )
        ).strip().lower()

        if action not in {
            "append",
            "set",
        }:
            action = "append"

        try:
            impact = float(
                item.get(
                    "projected_impact",
                    0,
                )
                or 0
            )

        except (
            TypeError,
            ValueError,
        ):
            impact = 0

        impact = round(
            min(
                25,
                max(
                    0,
                    impact,
                ),
            ),
            1,
        )

        suggestion_id = str(
            item.get(
                "id",
                "",
            )
        ).strip()

        if not suggestion_id:
            suggestion_id = (
                f"suggestion_{index}"
            )

        normalized.append(
            {
                "id":
                    suggestion_id,

                "category":
                    str(
                        item.get(
                            "category",
                            "strategy",
                        )
                    ).strip()
                    or "strategy",

                "title":
                    str(
                        item.get(
                            "title",
                            "Strategy improvement",
                        )
                    ).strip()
                    or "Strategy improvement",

                "reason":
                    str(
                        item.get(
                            "reason",
                            "",
                        )
                    ).strip(),

                "field":
                    field,

                "action":
                    action,

                "value":
                    item.get(
                        "value"
                    ),

                "projected_impact":
                    impact,
            }
        )

    return {
        "current_score":
            current_score,

        "projected_score":
            projected_score,

        "summary":
            str(
                result.get(
                    "summary",
                    "",
                )
                or ""
            ).strip(),

        "disclaimer":
            str(
                result.get(
                    "disclaimer",
                    (
                        "AI strategy analysis is educational "
                        "decision-support only. A higher strategy "
                        "score does not guarantee profitability "
                        "or future trading performance."
                    ),
                )
                or (
                    "AI strategy analysis is educational "
                    "decision-support only. A higher strategy "
                    "score does not guarantee profitability "
                    "or future trading performance."
                )
            ).strip(),

        "suggestions":
            normalized,
    }


def improve_strategy(
    strategy,
) -> dict:
    if AI_PROVIDER == "gemini":
        result = (
            improve_strategy_gemini(
                strategy
            )
        )

    elif AI_PROVIDER == "openai":
        result = (
            improve_strategy_openai(
                strategy
            )
        )

    else:
        raise RuntimeError(
            f"Unsupported AI_PROVIDER: {AI_PROVIDER}"
        )

    return normalize_improvements(
        result
    )
