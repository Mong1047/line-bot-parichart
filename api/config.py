"""Configuration loader for Vercel environment (reads from environment variables)."""

import json
import os


class Settings:
    # LINE
    LINE_CHANNEL_ACCESS_TOKEN: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    LINE_CHANNEL_SECRET: str = os.getenv("LINE_CHANNEL_SECRET", "")

    # Google Gemini AI
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

    @property
    def is_line_configured(self) -> bool:
        return bool(self.LINE_CHANNEL_ACCESS_TOKEN and self.LINE_CHANNEL_SECRET)

    @property
    def is_sheet_configured(self) -> bool:
        return bool(self.GOOGLE_SHEET_CREDENTIALS_JSON and self.GOOGLE_SHEET_ID)

    @property
    def is_gemini_configured(self) -> bool:
        return bool(self.GEMINI_API_KEY)


settings = Settings()