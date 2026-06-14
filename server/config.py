"""Configuration loader from .env file and environment variables."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    # LINE
    LINE_CHANNEL_ACCESS_TOKEN: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    LINE_CHANNEL_SECRET: str = os.getenv("LINE_CHANNEL_SECRET", "")

    # Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Google Sheets
    GOOGLE_SHEET_CREDENTIALS_JSON: dict | None = None
    GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")

    def __init__(self):
        creds_raw = os.getenv("GOOGLE_SHEET_CREDENTIALS_JSON")
        if creds_raw:
            try:
                self.GOOGLE_SHEET_CREDENTIALS_JSON = json.loads(creds_raw)
            except json.JSONDecodeError:
                print("⚠️ GOOGLE_SHEET_CREDENTIALS_JSON is not valid JSON")
                self.GOOGLE_SHEET_CREDENTIALS_JSON = None

    # Server
    PORT: int = int(os.getenv("PORT", "8000"))

    @property
    def is_line_configured(self) -> bool:
        return bool(self.LINE_CHANNEL_ACCESS_TOKEN and self.LINE_CHANNEL_SECRET)

    @property
    def is_sheet_configured(self) -> bool:
        return bool(self.GOOGLE_SHEET_CREDENTIALS_JSON and self.GOOGLE_SHEET_ID)


settings = Settings()