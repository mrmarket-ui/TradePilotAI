import base64
import json
import mimetypes
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

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


def clean_json(raw: str) -> dict:
    raw = raw.strip()

    if raw.startswith("```json"):
        raw = raw[7:]

    elif raw.startswith("```"):
        raw = raw[3:]

    if raw.endswith("```"):
        raw = raw[:-3]

    return json.loads(
        raw.strip()
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
    )


def extract_pdf_text(
    path: str,
) -> str:
    reader = PdfReader(
        path
    )

    return "\n\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )


def extract_text_file(
    path: str,
) -> str:
    return Path(
        path
    ).read_text(
        encoding="utf-8",
        errors="ignore",
    )


def fetch_url_text(
    url: str,
) -> str:
    response = httpx.get(
        url,
        timeout=30,
        follow_redirects=True,
        headers={
            "User-Agent":
                "TradePilotAI/1.0",
        },
    )

    response.raise_for_status()

    return response.text[
        :100000
    ]


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


def extract_strategy_openai(
    text: str,
) -> dict:
    client = (
        get_openai_client()
    )

    response = (
        client.responses.create(
            model=OPENAI_MODEL,
            input=(
                "You are TradePilot AI "
                "Strategy Extractor.\n"
                + strategy_schema_prompt()
                + "\n\nSOURCE:\n"
                + text[:80000]
            ),
        )
    )

    return clean_json(
        response.output_text
    )


def extract_strategy_gemini(
    text: str,
) -> dict:
    client = (
        get_gemini_client()
    )

    prompt = (
        "You are TradePilot AI "
        "Strategy Extractor.\n\n"
        + strategy_schema_prompt()
        + "\n\nSOURCE:\n"
        + text[:80000]
    )

    response = (
        client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type=
                    "application/json",
                temperature=0.1,
            ),
        )
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned no strategy content."
        )

    return clean_json(
        response.text
    )


def extract_strategy(
    text: str,
) -> dict:
    if not text.strip():
        raise ValueError(
            "No readable strategy content found."
        )

    if AI_PROVIDER == "gemini":
        return (
            extract_strategy_gemini(
                text
            )
        )

    if AI_PROVIDER == "openai":
        return (
            extract_strategy_openai(
                text
            )
        )

    raise RuntimeError(
        f"Unsupported AI_PROVIDER: {AI_PROVIDER}"
    )


def extract_strategy_from_image_openai(
    path: str,
) -> dict:
    client = (
        get_openai_client()
    )

    mime = (
        mimetypes.guess_type(
            path
        )[0]
        or "image/jpeg"
    )

    encoded = (
        base64.b64encode(
            Path(
                path
            ).read_bytes()
        ).decode(
            "ascii"
        )
    )

    image_url = (
        f"data:{mime};base64,{encoded}"
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
                            "text": (
                                "Analyze this image as "
                                "a trading strategy "
                                "document, chart "
                                "annotation, trading-plan "
                                "screenshot or educational "
                                "trading material. "
                                "Extract only rules "
                                "actually visible or "
                                "clearly supported.\n\n"
                                + strategy_schema_prompt()
                            ),
                        },
                        {
                            "type":
                                "input_image",
                            "image_url":
                                image_url,
                        },
                    ],
                }
            ],
        )
    )

    return clean_json(
        response.output_text
    )


def extract_strategy_from_image_gemini(
    path: str,
) -> dict:
    client = (
        get_gemini_client()
    )

    image_path = Path(
        path
    )

    if not image_path.exists():
        raise FileNotFoundError(
            "Strategy image file not found."
        )

    mime = (
        mimetypes.guess_type(
            str(image_path)
        )[0]
        or "image/jpeg"
    )

    image_bytes = (
        image_path.read_bytes()
    )

    prompt = (
        "Analyze this image as a trading "
        "strategy document, chart annotation, "
        "trading-plan screenshot or educational "
        "trading material.\n\n"
        "Extract only rules actually visible "
        "or clearly supported by the image.\n\n"
        + strategy_schema_prompt()
    )

    response = (
        client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime,
                ),
            ],
            config=types.GenerateContentConfig(
                response_mime_type=
                    "application/json",
                temperature=0.1,
            ),
        )
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned no image analysis."
        )

    return clean_json(
        response.text
    )


def extract_strategy_from_image(
    path: str,
) -> dict:
    if AI_PROVIDER == "gemini":
        return (
            extract_strategy_from_image_gemini(
                path
            )
        )

    if AI_PROVIDER == "openai":
        return (
            extract_strategy_from_image_openai(
                path
            )
        )

    raise RuntimeError(
        f"Unsupported AI_PROVIDER: {AI_PROVIDER}"
    )
