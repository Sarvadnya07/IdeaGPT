"""
IdeaGPT AI Gateway — Normalized Provider Error Handler.
Translates proprietary vendor exceptions into standardized, client-safe error objects.
Never exposes raw stack traces, API keys, or internal provider payload fragments.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

class NormalizedAIError(BaseModel):
    error_code: str
    provider: str
    model: Optional[str] = None
    retryable: bool = False
    safe_message: str
    status_code: int = 500

class ErrorNormalizer:
    @classmethod
    def normalize_exception(
        cls,
        exc: Exception,
        provider: str = "unknown",
        model: Optional[str] = None
    ) -> NormalizedAIError:
        exc_name = type(exc).__name__.lower()
        exc_str = str(exc).lower()

        # 1. Authentication & BYOK Key Errors
        if "auth" in exc_str or "unauthorized" in exc_str or "api_key" in exc_str or "401" in exc_str or "403" in exc_str:
            return NormalizedAIError(
                error_code="AUTHENTICATION_ERROR",
                provider=provider,
                model=model,
                retryable=False,
                safe_message=f"Authentication failed for provider '{provider}'. Please verify your API key.",
                status_code=401
            )

        # 2. Rate Limits & Quotas
        if "rate" in exc_str or "quota" in exc_str or "429" in exc_str or "too many requests" in exc_str:
            return NormalizedAIError(
                error_code="RATE_LIMITED",
                provider=provider,
                model=model,
                retryable=True,
                safe_message=f"Rate limit reached for provider '{provider}'. Please retry shortly.",
                status_code=429
            )

        # 3. Timeouts
        if "timeout" in exc_str or "timed out" in exc_str:
            return NormalizedAIError(
                error_code="TIMEOUT",
                provider=provider,
                model=model,
                retryable=True,
                safe_message=f"Request to provider '{provider}' timed out.",
                status_code=504
            )

        # 4. Invalid Model
        if "model" in exc_str and ("not found" in exc_str or "invalid" in exc_str or "unknown" in exc_str or "unsupported" in exc_str):
            return NormalizedAIError(
                error_code="INVALID_MODEL",
                provider=provider,
                model=model,
                retryable=False,
                safe_message=f"Requested model '{model}' is not supported or active on provider '{provider}'.",
                status_code=400
            )

        # 5. Safety & Content Refusal
        if "safety" in exc_str or "content policy" in exc_str or "harmful" in exc_str or "blocked" in exc_str:
            return NormalizedAIError(
                error_code="SAFETY_REFUSAL",
                provider=provider,
                model=model,
                retryable=False,
                safe_message="Content was flagged by provider safety boundaries.",
                status_code=400
            )

        # 6. Context Window Limit
        if "context length" in exc_str or "maximum context" in exc_str or "token limit" in exc_str:
            return NormalizedAIError(
                error_code="CONTEXT_LIMIT",
                provider=provider,
                model=model,
                retryable=False,
                safe_message=f"Prompt exceeded model '{model}' context window capacity.",
                status_code=400
            )

        # 7. Generic Network / Provider Outage
        return NormalizedAIError(
            error_code="PROVIDER_UNAVAILABLE",
            provider=provider,
            model=model,
            retryable=True,
            safe_message=f"AI Provider '{provider}' is currently unavailable. Please try again later.",
            status_code=503
        )
