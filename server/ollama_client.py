"""Client for interacting with local Ollama API."""

import httpx
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


async def ask_ollama(
    user_message: str,
    product_context: str = "",
    temperature: float = 0.7,
) -> str:
    """Send a message to Ollama and get a response."""
    system_prompt = SYSTEM_PROMPT.format(product_context=product_context or "ไม่มีข้อมูลสินค้าในตอนนี้")

    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "ขอโทษครับ/คะ ตอบไม่ได้ในตอนนี้")
        except httpx.TimeoutException:
            return "ขออภัยครับ/คะ การตอบกลับช้าเกินไป กรุณาลองถามใหม่อีกครั้ง"
        except httpx.HTTPStatusError as e:
            return f"เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI (รหัส: {e.response.status_code})"
        except Exception as e:
            return f"ขออภัยครับ/คะ เกิดข้อผิดพลาด: {str(e)}"


async def check_ollama_health() -> bool:
    """Check if Ollama is running and the model is available."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_URL}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            return any(m["name"] == settings.OLLAMA_MODEL for m in models)
    except Exception:
        return False