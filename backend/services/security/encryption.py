import os
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

key = os.getenv("ENCRYPTION_KEY")

if not key:
    raise RuntimeError("ENCRYPTION_KEY not found in .env")

FERNET = Fernet(key.encode())


def encrypt(text: str) -> str:
    return FERNET.encrypt(text.encode()).decode()


def decrypt(text: str) -> str:
    return FERNET.decrypt(text.encode()).decode()