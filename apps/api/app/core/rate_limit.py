"""
IdeaGPT API — Rate Limiter & Abuse Protection Module

Features:
- Centralized Limiter using SlowAPI
- User-aware rate keying: Uses cryptographically verified `request.state.user_id` or `request.state.clerk_id` if set,
  falling back to client remote IP address via `get_remote_address`.
- Configurable limits via app settings (e.g. AI evaluation, write API, default API limits).
- Standardized HTTP 429 JSON response handler with Retry-After headers.
"""

import logging
from typing import Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings

logger = logging.getLogger(__name__)


def rate_limit_key_func(request: Request) -> str:
    """
    Derives the rate-limiting identity key.

    Priority:
    1. Cryptographically verified `request.state.user_id` or `request.state.clerk_id` (attached during auth).
    2. Fallback to client remote IP address.
    """
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"

    clerk_id = getattr(request.state, "clerk_id", None)
    if clerk_id:
        return f"user:{clerk_id}"

    return f"ip:{get_remote_address(request)}"


# Determine storage backend (Redis URL if configured, otherwise process-local in-memory)
storage_uri = settings.RATE_LIMIT_STORAGE_URL or settings.REDIS_URL

limiter = Limiter(
    key_func=rate_limit_key_func,
    storage_uri=storage_uri if storage_uri else None,
    enabled=settings.RATE_LIMIT_ENABLED and settings.APP_ENV != "test",
)


def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Standardized FastAPI HTTP 429 response handler.
    Matches IdeaGPT error schema and attaches a Retry-After header.
    """
    logger.warning(
        "Rate limit exceeded: path=%s ip=%s limit=%s",
        request.url.path,
        get_remote_address(request),
        exc.detail,
    )

    request_id = getattr(request.state, "request_id", "") or ""

    headers = {"x-request-id": request_id}
    retry_after = getattr(exc, "retry_after", None)
    if retry_after is not None:
        headers["Retry-After"] = str(int(retry_after))
    else:
        headers["Retry-After"] = "60"

    return JSONResponse(
        status_code=429,
        headers=headers,
        content={
            "type": "https://httpstatuses.com/429",
            "title": "Too Many Requests",
            "status": 429,
            "detail": str(exc.detail) if exc.detail else "Too many requests",
            "request_id": request_id,
            # Backward-compatible fields
            "error": "Rate limit exceeded. Please wait before retrying.",
            "code": "RATE_LIMIT_EXCEEDED",
        },
    )
