import base64
import json
import mimetypes
import os
from pathlib import Path

from openai import OpenAI


def get_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return OpenAI(
        api_key=key,
    )


def get_model() -> str:
    model = os.getenv("OPENAI_MODEL")

    if not model:
        raise RuntimeError(
            "OPENAI_MODEL is not configured."
        )

    return model


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
        "name": strategy.name,
        "markets": strategy.markets,
        "allowed_symbols":
            strategy.allowed_symbols,
        "blocked_symbols":
            strategy.blocked_symbols,
        "preferred_direction":
            strategy.preferred_direction,
        "sessions": strategy.sessions,
        "timeframes": strategy.timeframes,
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


def analyze_chart(
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
        Path(image_path).read_bytes()
    ).decode("ascii")

    data_url = (
        f"data:{mime};base64,{encoded}"
    )

    prompt = f"""
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

    client = get_client()

    response = client.responses.create(
        model=get_model(),
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

    result = clean_json(
        response.output_text
    )

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

    result["direction"] = direction

    result["confidence"] = min(
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

    result["setup_score"] = min(
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

    return result
