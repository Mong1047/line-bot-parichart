import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from linebot.v3.exceptions import InvalidSignatureError
from line_handler import handler

app = FastAPI()


@app.post("/api/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Line-Signature", "")
    if not signature:
        return JSONResponse(status_code=400, content={"error": "Missing X-Line-Signature"})
    try:
        handler.handle(body.decode("utf-8"), signature)
        return JSONResponse(status_code=200, content={"status": "ok"})
    except InvalidSignatureError:
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})
    except Exception as e:
        print(f"Webhook error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
