"""
Vercel Serverless Function Entrypoint for IdeaGPT FastAPI Backend (Root Deployment).
Exposes the canonical FastAPI 'app' from apps/api/app/main.py.
"""
import sys
from pathlib import Path

# Add apps/api directory to sys.path so 'app.*' imports resolve cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
API_DIR = ROOT_DIR / "apps" / "api"

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from app.main import app  # noqa: E402

handler = app
__all__ = ["app", "handler"]
