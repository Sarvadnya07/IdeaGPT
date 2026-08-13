import asyncio
import logging
import random
import time
from typing import Callable, Any, TypeVar
from app.ai.exceptions.ai_exceptions import (
    AIException,
    AIRateLimitException,
    AITimeoutException,
    AINetworkException,
    AIUnavailableException
)

logger = logging.getLogger(__name__)
T = TypeVar("T")

class AIRetryPolicy:
    CONNECT_TIMEOUT_SEC: float = 5.0
    READ_TIMEOUT_SEC: float = 30.0
    OVERALL_TIMEOUT_SEC: float = 60.0
    MAX_ATTEMPTS: int = 3
    MIN_DELAY_SEC: float = 1.0
    MAX_DELAY_SEC: float = 5.0
    BACKOFF_FACTOR: float = 2.0

    @classmethod
    async def execute_with_retry(cls, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Executes an async function with bounded exponential backoff retries for transient errors.
        Fails fast on permanent non-retryable errors (401, 400, invalid keys/prompts).
        """
        attempt = 0
        last_exception = None

        while attempt < cls.MAX_ATTEMPTS:
            attempt += 1
            start_time = time.time()
            try:
                # Enforce overall timeout threshold
                return await asyncio.wait_for(func(*args, **kwargs), timeout=cls.OVERALL_TIMEOUT_SEC)

            except asyncio.TimeoutError as exc:
                last_exception = AITimeoutException(f"Execution timed out after {cls.OVERALL_TIMEOUT_SEC}s on attempt {attempt}")
                logger.warning(f"[Attempt {attempt}/{cls.MAX_ATTEMPTS}] Timeout: {str(last_exception)}")

            except AIException as exc:
                last_exception = exc
                if not exc.is_retryable:
                    logger.error(f"[Attempt {attempt}/{cls.MAX_ATTEMPTS}] Non-retryable error ({exc.code}): {exc.message}")
                    raise exc
                logger.warning(f"[Attempt {attempt}/{cls.MAX_ATTEMPTS}] Transient error ({exc.code}): {exc.message}")

            except Exception as exc:
                # Classify unknown exceptions
                err_str = str(exc).lower()
                if "429" in err_str or "rate limit" in err_str:
                    last_exception = AIRateLimitException(f"Rate limited upstream: {str(exc)}")
                elif "timeout" in err_str:
                    last_exception = AITimeoutException(f"Upstream timeout: {str(exc)}")
                elif "connect" in err_str or "connection" in err_str:
                    last_exception = AINetworkException(f"Upstream network error: {str(exc)}")
                else:
                    logger.error(f"[Attempt {attempt}/{cls.MAX_ATTEMPTS}] Permanent failure: {str(exc)}")
                    raise AIException(f"Provider execution error: {str(exc)}", status_code=500, is_retryable=False)

            if attempt < cls.MAX_ATTEMPTS:
                # Exponential backoff with jitter
                delay = min(cls.MAX_DELAY_SEC, cls.MIN_DELAY_SEC * (cls.BACKOFF_FACTOR ** (attempt - 1)))
                jitter = random.uniform(0.1, 0.5)
                total_delay = delay + jitter
                logger.info(f"Retrying provider call in {total_delay:.2f}s (Attempt {attempt + 1}/{cls.MAX_ATTEMPTS})...")
                await asyncio.sleep(total_delay)

        logger.error(f"Exhausted all {cls.MAX_ATTEMPTS} attempts for AI provider execution.")
        raise last_exception or AIException("Provider execution failed after maximum retries.", status_code=500)
