import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from fastapi import FastAPI
from config import settings

app = FastAPI()


@app.get("/api")
@app.get("/api/")
async def health():
    return {"status": "ok", "ai": "openrouter"}
