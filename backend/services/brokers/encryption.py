import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("ENCRYPTION_KEY")

if not key:
    raise RuntimeError(
        "ENCRYPTION_KEY is missing from the .env file."
    )

FERNET = Fernet(key.encode())


def encrypt(text: str) -> str:
    return FERNET.encrypt(text.encode()).decode()


def decrypt(text: str) -> str:
    return FERNET.decrypt(text.encode()).decode()