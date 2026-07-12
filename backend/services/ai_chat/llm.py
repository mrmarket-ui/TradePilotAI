"""
TradePilot AI LLM client.

Generates grounded coaching responses using the OpenAI Responses API.
"""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from services.ai_chat.prompts import SYSTEM_PROMPT


load_dotenv()


class LLMConfigurationError(RuntimeError):
    """Raised when the LLM is not configured correctly."""


def _json_context(context: dict[str, Any]) -> str:
    return json.dumps(
        context,
        ensure_ascii=False,
        default=str,
        indent=2,
    )


def is_llm_configured() -> bool:
    return bool(
        os.getenv("OPENAI_API_KEY", "").strip()
    )


def generate_llm_reply(
    message: str,
    context: dict[str, Any],
) -> str:
    """
    Generate a response grounded only in the trader's analytics.
    """

    api_key = os.getenv(
        "OPENAI_API_KEY",
        "",
    ).strip()

    if not api_key:
        raise LLMConfigurationError(
            "OPENAI_API_KEY is not configured."
        )

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5-mini",
    ).strip()

    client = OpenAI(
        api_key=api_key,
        timeout=45.0,
        max_retries=2,
    )

    trader_context = _json_context(context)

    user_input = f"""
TRADER DATA
-----------
{trader_context}

USER QUESTION
-------------
{message}

INSTRUCTIONS
------------
Answer only from the trader data above.

If the available data is insufficient, clearly say that.

Do not promise profits or guarantee trading results.

Identify the most important issue first.

Give practical actions the trader can apply immediately.

Keep the response under 300 words.
""".strip()

    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=user_input,
        max_output_tokens=600,
    )

    answer = response.output_text.strip()

    if not answer:
        raise RuntimeError(
            "The AI provider returned an empty response."
        )

    return answer
