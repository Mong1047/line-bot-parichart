"""FastAPI server for Parichart Plant Shop LINE OA Bot."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from linebot.v3.exceptions import InvalidSignatureError

from config import settings
from line_handler import handler
from ollama_client import check_ollama_health
from sheet_rag import sheet_rag


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: check Ollama health
    ollama_ok = await check_ollama_health()
    if ollama_ok:
        print(f"✅ Ollama connected — model: {settings.OLLAMA_MODEL}")
    else:
        print(f"⚠️ Ollama not ready — model '{settings.OLLAMA_MODEL}' not found")

    # Check Google Sheets
    if settings.is_sheet_configured:
        products = sheet_rag.get_all_products()
        print(f"✅ Google Sheet connected — {len(products)} products loaded")
    else:
        print("ℹ️ Google Sheet not configured — will run without product data")

    yield
    # Shutdown
    print("👋 Server shutting down")


app = FastAPI(
    title="สวนปาริชาติ LINE OA Bot",
    description="AI chatbot for ร้านสวนปาริชาติ using Ollama + Google Sheets",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Health check endpoint."""
    ollama_ok = await check_ollama_health()
    return {
        "status": "ok",
        "ollama": ollama_ok,
        "model": settings.OLLAMA_MODEL,
        "sheet_configured": settings.is_sheet_configured,
    }


@app.post("/webhook")
async def webhook(request: Request):
    """LINE webhook endpoint."""
    # Get request body as text
    body = await request.body()
    body_str = body.decode("utf-8")

    # Get signature from headers
    signature = request.headers.get("X-Line-Signature", "")

    if not signature:
        return JSONResponse(
            status_code=400, content={"error": "Missing X-Line-Signature header"}
        )

    try:
        # Handle the webhook event
        handler.handle(body_str, signature)
        return JSONResponse(status_code=200, content={"status": "ok"})
    except InvalidSignatureError:
        return JSONResponse(
            status_code=400, content={"error": "Invalid signature"}
        )
    except Exception as e:
        print(f"⚠️ Webhook error: {e}")
        return JSONResponse(
            status_code=500, content={"error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn

    print(f"🚀 Starting สวนปาริชาติ LINE OA Bot on port {settings.PORT}")
    print(f"   Model: {settings.OLLAMA_MODEL}")
    print(f"   LINE configured: {settings.is_line_configured}")
    print(f"   Sheet configured: {settings.is_sheet_configured}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=False,
    )