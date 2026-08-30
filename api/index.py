"""
Vercel Serverless Function Entrypoint for IdeaGPT FastAPI Backend.
Exports canonical 'app' instance from apps/api/app.main.
"""
import sys
from pathlib import Path

# Ensure repo root and apps/api are in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
APPS_API_DIR = REPO_ROOT / "apps" / "api"

for path in (str(APPS_API_DIR), str(REPO_ROOT), str(CURRENT_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from apps.api.app.main import app  # noqa: E402
except ImportError:
    from app.main import app  # noqa: E402

__all__ = ["app"]
