"""
Vercel Serverless Function Entrypoint for IdeaGPT FastAPI Backend.
Exports 'app' instance from app.main.
"""
import json
import logging
import sys
import traceback
from pathlib import Path

# Ensure apps/api directory is on sys.path so 'app.*' imports resolve cleanly
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

logger = logging.getLogger("ideagpt.entrypoint")

try:
    from app.main import app
    handler = app
except Exception as exc:
    exc_type_name = type(exc).__name__
    exc_message = str(exc)
    import_error_traceback = traceback.format_exc()
    logger.critical(f"FATAL: Failed to import FastAPI application: {exc}\n{import_error_traceback}")

    # Fallback ASGI application to expose the exact import error
    async def app(scope, receive, send):
        if scope["type"] == "http":
            body = json.dumps({
                "status": "error",
                "phase": "import",
                "error_type": exc_type_name,
                "error_message": exc_message,
                "traceback": import_error_traceback.splitlines(),
                "python_version": sys.version,
                "sys_path": sys.path,
            }).encode("utf-8")
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("utf-8")),
                ],
            })
            await send({
                "type": "http.response.body",
                "body": body,
            })

    handler = app

__all__ = ["app", "handler"]


