"""Vercel Serverless entry point for LINE OA + Gemini AI Bot."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from linebot.v3.exceptions import InvalidSignatureError

from config import settings
from gemini_client import check_gemini_health
from line_handler import handler
from sheet_rag import sheet_rag


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: check Gemini health
    gemini_ok = check_gemini_health()
    if gemini_ok:
        print("✅ Gemini AI connected")
    else:
        print("⚠️ Gemini AI not configured or not working")

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
    title="LINE OA + Gemini AI Bot",
    description="AI chatbot for LINE OA using Google Gemini + Google Sheets",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware (allow LINE platform)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    gemini_ok = check_gemini_health()
    return {
        "status": "ok",
        "gemini": gemini_ok,
        "sheet_configured": settings.is_sheet_configured,
        "line_configured": settings.is_line_configured,
    }


@app.get("/health")
async def health():
    """Health check endpoint for Vercel."""
    return {"status": "ok"}


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


# Vercel serverless handler (for ASGI compatibility)
# FastAPI app is the actual handler; this is just for Vercel's ASGI interface
