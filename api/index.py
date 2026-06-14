import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

try:
    from main import app
except Exception as _e:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST"])
    async def _err(path: str = ""):
        return JSONResponse({"error": str(_e), "type": type(_e).__name__}, status_code=500)
