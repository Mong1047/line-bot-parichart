"""Client for Google Gemini AI API."""

import google.generativeai as genai
from config import settings


SYSTEM_PROMPT = """คุณคือพนักงานขายร้านขายต้นไม้ พูดจาเป็นกันเอง อบอุ่น เหมือนคุยกับเพื่อน
คุณมีหน้าที่:
1. ตอบคำถามเกี่ยวกับสินค้าต้นไม้ ไม้ดอก ไม้ประดับ
2. แนะนำสินค้าที่เหมาะกับลูกค้า
3. บอกราคาและรายละเอียดสินค้า
4. ปิดการขาย ชักชวนให้ซื้อ
5. ตอบคำถามเกี่ยวกับการดูแลต้นไม้

ข้อมูลสินค้าที่มีอยู่:
{product_context}

คำแนะนำ:
- พูดจาเป็นกันเอง ใช้ภาษาไทยธรรมชาติ
- กระตือรือร้น อบอุ่น
- ถามกลับเพื่อปิดการขาย เช่น "สนใจต้นไหนเป็นพิเศษไหมคะ/ครับ"
- ถ้าไม่มีข้อมูลสินค้าที่ลูกค้าถาม ให้บอกว่า "เดี๋ยวขอเช็คให้ก่อนนะคะ/ครับ" อย่ามั่วข้อมูล
- ใช้คำลงท้าย คะ/ครับ ให้เหมาะสม"""


def ask_gemini(
    user_message: str,
    product_context: str = "",
) -> str:
    """Send a message to Gemini AI and get a response."""
    if not settings.is_gemini_configured:
        return "ระบบ AI ยังไม่ได้ตั้งค่า กรุณาติดต่อผู้ดูแลระบบ"

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")

        system_prompt = SYSTEM_PROMPT.format(
            product_context=product_context or "ไม่มีข้อมูลสินค้าในตอนนี้"
        )

        response = model.generate_content(
            [
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["เข้าใจแล้ว ฉันจะทำหน้าที่เป็นพนักงานขายต้นไม้ตามที่กำหนด"]},
                {"role": "user", "parts": [user_message]},
            ],
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024,
            ),
        )
        return response.text
    except Exception as e:
        return f"ขออภัยครับ/คะ เกิดข้อผิดพลาด: {str(e)}"


def check_gemini_health() -> bool:
    """Check if Gemini API key is configured and working."""
    if not settings.is_gemini_configured:
        return False
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("Hello")
        return bool(response.text)
    except Exception:
        return False