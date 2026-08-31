import sys
from pathlib import Path

# Ensure apps/api is in sys.path so internal app.* modules resolve
_apps_api_dir = str(Path(__file__).resolve().parent.parent / "apps" / "api")
if _apps_api_dir not in sys.path:
    sys.path.insert(0, _apps_api_dir)

from app.main import app

__all__ = ["app"]
