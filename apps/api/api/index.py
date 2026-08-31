import sys
from pathlib import Path

# Add apps/api directory to sys.path so 'app.*' imports resolve cleanly
CURRENT_DIR = Path(__file__).resolve().parent.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from app.main import app

__all__ = ["app"]
