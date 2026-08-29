"""
Vercel Serverless Function entrypoint for IdeaGPT FastAPI backend.
Exports 'app' instance from apps.api.app.main.
"""
import sys
from pathlib import Path

# Ensure apps/api directory is on sys.path so 'app.*' imports resolve cleanly
REPO_ROOT = Path(__file__).resolve().parent.parent
API_DIR = REPO_ROOT / "apps" / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from app.main import app  # noqa: E402

__all__ = ["app"]
