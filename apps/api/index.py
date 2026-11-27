# Vercel serverless entry point.
# NOTE: apps/api/api/index.py is a byte-identical twin of this file. Vercel's
# build output has historically resolved entry modules from different roots
# depending on configuration; keep both until deployment is confirmed stable,
# then delete one. Do not edit one without the other.
import sys
from pathlib import Path

# Robust sys.path resolution for all Vercel execution contexts
_here = Path(__file__).resolve().parent
_candidates = [
    _here,
    _here.parent,
    _here.parent / "apps" / "api",
    Path.cwd(),
    Path("/var/task"),
    Path("/var/task/apps/api"),
]

for _p in _candidates:
    _p_str = str(_p)
    if _p_str not in sys.path:
        sys.path.insert(0, _p_str)

from app.main import app

__all__ = ["app"]
