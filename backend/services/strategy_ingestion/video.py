import os
import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg
from openai import OpenAI


TRANSCRIPTION_MODEL = os.getenv(
    "OPENAI_TRANSCRIPTION_MODEL",
    "gpt-4o-mini-transcribe",
)


def get_client() -> OpenAI:
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


def extract_audio(
    video_path: str,
) -> str:
    ffmpeg = (
        imageio_ffmpeg
        .get_ffmpeg_exe()
    )

    source = Path(
        video_path
    )

    if not source.exists():
        raise FileNotFoundError(
            "Video file not found."
        )

    temporary = tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False,
    )

    audio_path = (
        temporary.name
    )

    temporary.close()

    command = [
        ffmpeg,
        "-y",
        "-i",
        str(source),
        "-vn",
        "-acodec",
        "libmp3lame",
        "-ar",
        "16000",
        "-ac",
        "1",
        "-b:a",
        "64k",
        audio_path,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        Path(
            audio_path
        ).unlink(
            missing_ok=True,
        )

        raise RuntimeError(
            "Unable to extract audio "
            "from video."
        )

    return audio_path


def transcribe_video(
    video_path: str,
) -> str:
    audio_path = extract_audio(
        video_path
    )

    client = get_client()

    try:
        with open(
            audio_path,
            "rb",
        ) as audio:
            response = (
                client
                .audio
                .transcriptions
                .create(
                    model=
                        TRANSCRIPTION_MODEL,
                    file=audio,
                )
            )

        text = getattr(
            response,
            "text",
            None,
        )

        if not text:
            raise RuntimeError(
                "Video transcription "
                "returned no text."
            )

        return text.strip()

    finally:
        Path(
            audio_path
        ).unlink(
            missing_ok=True,
        )
