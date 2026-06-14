import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from config import settings

app = FastAPI()


@app.post("/api/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Line-Signature", "MISSING")
    return JSONResponse({
        "status": "debug",
        "sig_present": signature != "MISSING",
        "sig_len": len(signature),
        "body_len": len(body),
        "secret_set": bool(settings.LINE_CHANNEL_SECRET),
        "secret_len": len(settings.LINE_CHANNEL_SECRET),
    }, status_code=200)
