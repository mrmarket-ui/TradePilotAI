import base64
import json
import mimetypes
import os
from pathlib import Path

import httpx
from openai import OpenAI
from pypdf import PdfReader


MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-terra",
)


def get_openai_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return OpenAI(api_key=key)


def clean_json(raw: str) -> dict:
    raw = raw.strip()

    if raw.startswith("```json"):
        raw = raw[7:]

    elif raw.startswith("```"):
        raw = raw[3:]

    if raw.endswith("```"):
        raw = raw[:-3]

    return json.loads(raw.strip())


def extract_pdf_text(path: str) -> str:
    reader = PdfReader(path)

    return "\n\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )


def extract_text_file(path: str) -> str:
    return Path(path).read_text(
        encoding="utf-8",
        errors="ignore",
    )


def fetch_url_text(url: str) -> str:
    response = httpx.get(
        url,
        timeout=30,
        follow_redirects=True,
        headers={
            "User-Agent": "TradePilotAI/1.0",
        },
    )

    response.raise_for_status()

    return response.text[:100000]


def strategy_schema_prompt() -> str:
    return """
Return valid JSON only.

Extract the trading strategy without inventing
rules that are not supported by the source.

Required JSON structure:

{
  "name": null,
  "description": null,
  "strategy_type": null,
  "markets": [],
  "allowed_symbols": [],
  "blocked_symbols": [],
  "preferred_direction": "BOTH",
  "sessions": [],
  "timeframes": [],
  "allowed_weekdays": [],
  "trading_start_time": null,
  "trading_end_time": null,
  "timezone": null,
  "entry_rules": [],
  "confirmations": [],
  "exit_rules": [],
  "psychology_rules": [],
  "trade_management_rules": [],
  "pre_trade_checklist": [],
  "post_trade_checklist": [],
  "max_risk_percent": null,
  "min_risk_reward": null,
  "max_daily_loss_percent": null,
  "max_weekly_loss_percent": null,
  "max_trades_per_day": null,
  "max_consecutive_losses": null,
  "max_open_positions": null,
  "move_to_breakeven_at_rr": null,
  "partial_take_profit_percent": null,
  "avoid_high_impact_news": null,
  "news_minutes_before": null,
  "news_minutes_after": null,
  "ai_notes": null
}
"""


def extract_strategy(text: str) -> dict:
    if not text.strip():
        raise ValueError(
            "No readable strategy content found."
        )

    client = get_openai_client()

    response = client.responses.create(
        model=MODEL,
        input=(
            "You are TradePilot AI Strategy Extractor.\n"
            + strategy_schema_prompt()
            + "\n\nSOURCE:\n"
            + text[:80000]
        ),
    )

    return clean_json(
        response.output_text
    )


def extract_strategy_from_image(
    path: str,
) -> dict:
    client = get_openai_client()

    mime = (
        mimetypes.guess_type(path)[0]
        or "image/jpeg"
    )

    encoded = base64.b64encode(
        Path(path).read_bytes()
    ).decode("ascii")

    image_url = (
        f"data:{mime};base64,{encoded}"
    )

    response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Analyze this image as a trading "
                            "strategy document, chart annotation, "
                            "trading-plan screenshot or educational "
                            "trading material. Extract only rules "
                            "actually visible or clearly supported.\n\n"
                            + strategy_schema_prompt()
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url,
                    },
                ],
            }
        ],
    )

    return clean_json(
        response.output_text
    )
