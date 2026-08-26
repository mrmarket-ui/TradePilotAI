import base64
import json
import mimetypes
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from google import genai
from google.genai import types


load_dotenv()


AI_PROVIDER = os.getenv(
    "AI_PROVIDER",
    "gemini",
).strip().lower()


OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-terra",
)


GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)


def get_openai_client() -> OpenAI:
    key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return OpenAI(
        api_key=key,
    )


def get_gemini_client():
    key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=key,
        http_options=types.HttpOptions(
            timeout=20000,
            retry_options=
                types.HttpRetryOptions(
                    attempts=1,
                ),
        ),
    )


def clean_json(
    raw: str,
) -> dict:
    value = raw.strip()

    if value.startswith("```json"):
        value = value[7:]

    elif value.startswith("```"):
        value = value[3:]

    if value.endswith("```"):
        value = value[:-3]

    return json.loads(
        value.strip()
    )


def strategy_context(
    strategy,
) -> dict:
    return {
        "name":
            strategy.name,

        "markets":
            strategy.markets,

        "allowed_symbols":
            strategy.allowed_symbols,

        "blocked_symbols":
            strategy.blocked_symbols,

        "preferred_direction":
            strategy.preferred_direction,

        "sessions":
            strategy.sessions,

        "timeframes":
            strategy.timeframes,

        "entry_rules":
            strategy.entry_rules,

        "confirmations":
            strategy.confirmations,

        "exit_rules":
            strategy.exit_rules,

        "trade_management_rules":
            strategy.trade_management_rules,

        "max_risk_percent":
            strategy.max_risk_percent,

        "min_risk_reward":
            strategy.min_risk_reward,

        "max_trades_per_day":
            strategy.max_trades_per_day,

        "max_consecutive_losses":
            strategy.max_consecutive_losses,
    }


def build_prompt(
    strategy,
    symbol: str,
    timeframe: str,
) -> str:
    return f"""
You are TradePilot AI's strategy-validation engine.

Analyze the uploaded trading chart ONLY against
the user's supplied strategy rules.

Do not invent market data that cannot be seen.
Do not force a trade.

A NO_TRADE result is correct whenever the setup
does not satisfy the strategy strongly enough.

SYMBOL:
{symbol}

TIMEFRAME:
{timeframe}

USER STRATEGY:
{json.dumps(strategy_context(strategy))}

Return valid JSON only:

{{
  "direction": "BUY | SELL | NO_TRADE",
  "confidence": 0,
  "setup_score": 0,
  "entry_low": null,
  "entry_high": null,
  "stop_loss": null,
  "take_profit_1": null,
  "take_profit_2": null,
  "take_profit_3": null,
  "risk_reward": null,
  "matched_rules": [],
  "missing_rules": [],
  "reasoning": "",
  "invalidation": ""
}}

Rules:

confidence must be 0-100.
setup_score must be 0-100.

If price levels cannot be read reliably,
use null rather than guessing.

Return NO_TRADE if required confirmations
or entry conditions are missing.

Never claim guaranteed profit.
"""


def analyze_chart_openai(
    image_path: str,
    strategy,
    symbol: str,
    timeframe: str,
) -> dict:
    mime = (
        mimetypes.guess_type(
            image_path
        )[0]
        or "image/jpeg"
    )

    encoded = base64.b64encode(
        Path(
            image_path
        ).read_bytes()
    ).decode(
        "ascii"
    )

    data_url = (
        f"data:{mime};base64,{encoded}"
    )

    prompt = build_prompt(
        strategy,
        symbol,
        timeframe,
    )

    client = (
        get_openai_client()
    )

    response = (
        client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type":
                                "input_text",
                            "text":
                                prompt,
                        },
                        {
                            "type":
                                "input_image",
                            "image_url":
                                data_url,
                        },
                    ],
                },
            ],
        )
    )

    return clean_json(
        response.output_text
    )


def analyze_chart_gemini(
    image_path: str,
    strategy,
    symbol: str,
    timeframe: str,
) -> dict:
    image = Path(
        image_path
    )

    if not image.exists():
        raise FileNotFoundError(
            "Chart image file not found."
        )

    mime = (
        mimetypes.guess_type(
            str(image)
        )[0]
        or "image/jpeg"
    )

    prompt = build_prompt(
        strategy,
        symbol,
        timeframe,
    )

    client = (
        get_gemini_client()
    )

    response = (
        client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                prompt,

                types.Part.from_bytes(
                    data=image.read_bytes(),
                    mime_type=mime,
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
            "Gemini returned no signal analysis."
        )

    return clean_json(
        response.text
    )


def normalize_result(
    result: dict,
) -> dict:
    direction = str(
        result.get(
            "direction",
            "NO_TRADE",
        )
    ).upper()

    if direction not in {
        "BUY",
        "SELL",
        "NO_TRADE",
    }:
        direction = "NO_TRADE"

    result[
        "direction"
    ] = direction


    result[
        "confidence"
    ] = min(
        100,
        max(
            0,
            float(
                result.get(
                    "confidence",
                    0,
                )
                or 0
            ),
        ),
    )


    result[
        "setup_score"
    ] = min(
        100,
        max(
            0,
            float(
                result.get(
                    "setup_score",
                    0,
                )
                or 0
            ),
        ),
    )


    if not isinstance(
        result.get(
            "matched_rules"
        ),
        list,
    ):
        result[
            "matched_rules"
        ] = []


    if not isinstance(
        result.get(
            "missing_rules"
        ),
        list,
    ):
        result[
            "missing_rules"
        ] = []


    return result


def analyze_chart(
    image_path: str,
    strategy,
    symbol: str,
    timeframe: str,
) -> dict:
    if AI_PROVIDER == "gemini":
        result = (
            analyze_chart_gemini(
                image_path=image_path,
                strategy=strategy,
                symbol=symbol,
                timeframe=timeframe,
            )
        )

    elif AI_PROVIDER == "openai":
        result = (
            analyze_chart_openai(
                image_path=image_path,
                strategy=strategy,
                symbol=symbol,
                timeframe=timeframe,
            )
        )

    else:
        raise RuntimeError(
            f"Unsupported AI_PROVIDER: {AI_PROVIDER}"
        )

    return normalize_result(
        result
    )
