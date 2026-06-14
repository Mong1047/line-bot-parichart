"""Read product data from Google Sheet and build context for AI."""

import json
from typing import Optional

import gspread
from google.auth import exceptions as google_auth_exceptions
from google.oauth2 import service_account
from config import settings


class SheetRAG:
    """Retrieve product information from Google Sheets."""

    def __init__(self):
        self._client: Optional[gspread.Client] = None
        self._products_cache: list[dict] = []
        self._cache_timestamp: float = 0

    def _get_client(self) -> Optional[gspread.Client]:
        """Get or create the Google Sheets client."""
        if self._client:
            return self._client

        if not settings.is_sheet_configured:
            return None

        try:
            creds = service_account.Credentials.from_service_account_info(
                settings.GOOGLE_SHEET_CREDENTIALS_JSON,
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
            )
            self._client = gspread.authorize(creds)
            return self._client
        except (json.JSONDecodeError, google_auth_exceptions.GoogleAuthError) as e:
            print(f"⚠️ Google Sheets auth error: {e}")
            return None

    def get_all_products(self) -> list[dict]:
        """Fetch all products from the Google Sheet."""
        client = self._get_client()
        if not client:
            return []

        try:
            sheet = client.open_by_key(settings.GOOGLE_SHEET_ID)
            worksheet = sheet.sheet1  # First sheet
            records = worksheet.get_all_records()

            self._products_cache = records
            return records
        except Exception as e:
            print(f"⚠️ Error reading Google Sheet: {e}")
            return self._products_cache  # Return cache if available

    def build_product_context(self, max_chars: int = 3000) -> str:
        """Build a text summary of all products for the AI prompt."""
        products = self.get_all_products()
        if not products:
            return ""

        lines = []
        total_chars = 0

        for i, product in enumerate(products, 1):
            # Handle flexible column names (thai or english)
            name = product.get("name") or product.get("ชื่อสินค้า") or product.get("ชื่อ", "")
            price = product.get("price") or product.get("ราคา", "")
            category = product.get("category") or product.get("หมวดหมู่", "")
            detail = product.get("detail") or product.get("รายละเอียด", "")
            stock = product.get("stock") or product.get("จำนวนคงเหลือ", "")

            line = f"{i}. {name}"
            if category:
                line += f" ({category})"
            if price:
                line += f" - ราคา {price} บาท"
            if detail:
                line += f" | {detail[:100]}"
            if stock:
                line += f" | คงเหลือ: {stock}"
            line += "\n"

            if total_chars + len(line) > max_chars:
                break

            lines.append(line)
            total_chars += len(line)

        return "รายการสินค้า:\n" + "".join(lines)

    def search_products(self, query: str) -> str:
        """Search products by keyword and return matching results."""
        products = self.get_all_products()
        if not products:
            return ""

        query_lower = query.lower()
        matches = []

        for product in products:
            name = str(product.get("name") or product.get("ชื่อสินค้า") or product.get("ชื่อ", "")).lower()
            detail = str(product.get("detail") or product.get("รายละเอียด", "")).lower()
            category = str(product.get("category") or product.get("หมวดหมู่", "")).lower()

            if query_lower in name or query_lower in detail or query_lower in category:
                match_name = product.get("name") or product.get("ชื่อสินค้า") or product.get("ชื่อ", "")
                match_price = product.get("price") or product.get("ราคา", "")
                match_detail = product.get("detail") or product.get("รายละเอียด", "")
                match_stock = product.get("stock") or product.get("จำนวนคงเหลือ", "")

                line = f"• {match_name}"
                if match_price:
                    line += f" — ราคา {match_price} บาท"
                if match_detail:
                    line += f"\n  {match_detail[:150]}"
                if match_stock:
                    line += f"\n  คงเหลือ: {match_stock}"
                matches.append(line)

        if not matches:
            return ""

        return "สินค้าที่เกี่ยวข้อง:\n" + "\n\n".join(matches)


sheet_rag = SheetRAG()