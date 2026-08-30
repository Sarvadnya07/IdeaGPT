"""
Vercel Serverless Function Entrypoint for IdeaGPT FastAPI Backend.
Exports 'app' instance from app.main.
"""
import sys
from pathlib import Path

# Ensure apps/api directory is on sys.path so 'app.*' imports resolve cleanly
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from app.main import app  # noqa: E402

handler = app
__all__ = ["app", "handler"]

