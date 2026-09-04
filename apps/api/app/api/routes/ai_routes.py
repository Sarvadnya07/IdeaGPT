"""
Backward-compatibility bridge for AI routes.
Re-exports the modular router from app.api.routes.ai.
"""

from app.api.routes.ai import router

__all__ = ["router"]
