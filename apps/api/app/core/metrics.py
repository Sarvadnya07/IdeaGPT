"""
IdeaGPT API — Prometheus & Operational Metrics Engine

Implements low-overhead, thread-safe Prometheus metrics instrumentation:
- Dedicated Prometheus text exposition format (version 0.0.4).
- Strictly bounded cardinality labels:
    - HTTP metrics: method, route, status_code
    - AI metrics: provider, operation, status
- Path parameter normalization preventing label explosion:
    - Dynamic UUIDs, IDs, and query parameters are collapsed to `{id}`.
    - Matches FastAPI declared route templates whenever matched.
- Failure-safe design:
    - Instrumentation errors never fail API requests.
- Zero secret, tenant, user, or payload leakage in metric labels.
"""

import time
import re
import logging
from typing import Optional, Dict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

import prometheus_client
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

logger = logging.getLogger("ideagpt.metrics")

# Dedicated registry for IdeaGPT API to ensure clean isolation
metrics_registry = CollectorRegistry(auto_describe=True)

# ---------------------------------------------------------------------------
# HTTP Request Metrics (Bounded Cardinality)
# ---------------------------------------------------------------------------

http_requests_total = Counter(
    "http_requests_total",
    "Total count of HTTP requests processed by the API",
    labelnames=["method", "route", "status_code"],
    registry=metrics_registry,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency distribution in seconds",
    labelnames=["method", "route", "status_code"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=metrics_registry,
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Current number of HTTP requests being processed concurrently",
    labelnames=["method", "route"],
    registry=metrics_registry,
)

# ---------------------------------------------------------------------------
# Abuse & Rate Limiting Metrics
# ---------------------------------------------------------------------------

ideagpt_rate_limit_exceeded_total = Counter(
    "ideagpt_rate_limit_exceeded_total",
    "Total count of rate limit exceeded events",
    labelnames=["route"],
    registry=metrics_registry,
)

# ---------------------------------------------------------------------------
# Application & AI Gateway Metrics
# ---------------------------------------------------------------------------

ideagpt_ai_requests_total = Counter(
    "ideagpt_ai_requests_total",
    "Total AI inference requests dispatched through AI Gateway",
    labelnames=["provider", "operation", "status"],
    registry=metrics_registry,
)

ideagpt_ai_fallback_total = Counter(
    "ideagpt_ai_fallback_total",
    "Total AI fallback events from primary to fallback provider",
    labelnames=["primary_provider", "fallback_provider"],
    registry=metrics_registry,
)

ideagpt_ai_request_duration_seconds = Histogram(
    "ideagpt_ai_request_duration_seconds",
    "AI Gateway provider inference duration in seconds",
    labelnames=["provider", "operation"],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
    registry=metrics_registry,
)

ideagpt_ai_tokens_total = Counter(
    "ideagpt_ai_tokens_total",
    "Total AI model tokens consumed",
    labelnames=["provider", "token_type"],
    registry=metrics_registry,
)

ideagpt_ai_tasks = Gauge(
    "ideagpt_ai_tasks",
    "Current count of AI background tasks in database by status",
    labelnames=["status"],
    registry=metrics_registry,
)


# ---------------------------------------------------------------------------
# Cardinality Protection & Route Normalization
# ---------------------------------------------------------------------------

_UUID_REGEX = re.compile(
    r"/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
_INTEGER_ID_REGEX = re.compile(r"/\d+(?=/|$)")


def normalize_route_path(raw_path: str) -> str:
    """
    Normalizes dynamic URL paths to static route templates with bounded cardinality.
    Prevents user IDs, UUIDs, or arbitrary path components from inflating label dimensions.
    """
    if not raw_path or raw_path == "/":
        return "/"

    # Strip query parameters if accidentally included in path
    path = raw_path.split("?")[0].strip()

    # Replace UUID path parameters with {id}
    normalized = _UUID_REGEX.sub("/{id}", path)

    # Replace integer path parameters with {id}
    normalized = _INTEGER_ID_REGEX.sub("/{id}", normalized)

    return normalized


def extract_route_label(request: Request) -> str:
    """
    Safely extracts the route label from a Starlette/FastAPI request.
    Prefers the matched FastAPI route template (e.g. `/api/v1/projects/{project_id}`).
    Falls back to normalized URL path.
    """
    try:
        route = request.scope.get("route")
        if route and hasattr(route, "path") and route.path:
            return str(route.path)
    except Exception:
        pass

    raw_path = request.url.path if hasattr(request, "url") else "/"
    return normalize_route_path(raw_path)


# ---------------------------------------------------------------------------
# Recording Helper Functions (Failure-Safe)
# ---------------------------------------------------------------------------

def record_rate_limit_exceeded(route_path: str) -> None:
    """Records a 429 rate limit exceeded event with normalized route label."""
    try:
        norm_route = normalize_route_path(route_path)
        ideagpt_rate_limit_exceeded_total.labels(route=norm_route).inc()
    except Exception as exc:
        logger.warning("Failed to record rate limit metric: %s", exc)


def record_ai_request(
    provider: str,
    operation: str = "generation",
    status: str = "success",
    duration_seconds: Optional[float] = None,
) -> None:
    """Records an AI Gateway request with bounded provider, operation, and status labels."""
    try:
        safe_provider = str(provider).lower()[:32] if provider else "unknown"
        safe_op = str(operation).lower()[:32] if operation else "unknown"
        safe_status = str(status).lower()[:32] if status else "unknown"

        ideagpt_ai_requests_total.labels(
            provider=safe_provider,
            operation=safe_op,
            status=safe_status,
        ).inc()

        if duration_seconds is not None and duration_seconds >= 0:
            ideagpt_ai_request_duration_seconds.labels(
                provider=safe_provider,
                operation=safe_op,
            ).observe(duration_seconds)
    except Exception as exc:
        logger.warning("Failed to record AI request metric: %s", exc)


def record_ai_fallback(primary_provider: str, fallback_provider: str) -> None:
    """Records an AI provider fallback occurrence."""
    try:
        safe_primary = str(primary_provider).lower()[:32] if primary_provider else "unknown"
        safe_fallback = str(fallback_provider).lower()[:32] if fallback_provider else "unknown"

        ideagpt_ai_fallback_total.labels(
            primary_provider=safe_primary,
            fallback_provider=safe_fallback,
        ).inc()
    except Exception as exc:
        logger.warning("Failed to record AI fallback metric: %s", exc)


def record_ai_tokens(provider: str, prompt_tokens: int = 0, completion_tokens: int = 0) -> None:
    """Records token consumption metrics by provider and token type."""
    try:
        safe_provider = str(provider).lower()[:32] if provider else "unknown"
        if prompt_tokens > 0:
            ideagpt_ai_tokens_total.labels(
                provider=safe_provider,
                token_type="prompt",
            ).inc(prompt_tokens)
        if completion_tokens > 0:
            ideagpt_ai_tokens_total.labels(
                provider=safe_provider,
                token_type="completion",
            ).inc(completion_tokens)
    except Exception as exc:
        logger.warning("Failed to record AI token metric: %s", exc)


def update_ai_tasks_gauge(counts_by_status: Dict[str, int]) -> None:
    """Updates AI task status gauge counts from database aggregates."""
    try:
        for status_name, count in counts_by_status.items():
            safe_status = str(status_name).lower()[:32]
            ideagpt_ai_tasks.labels(status=safe_status).set(count)
    except Exception as exc:
        logger.warning("Failed to update AI tasks gauge: %s", exc)


def get_prometheus_exposition_text() -> bytes:
    """Generates the formatted Prometheus text exposition payload."""
    return generate_latest(metrics_registry)


# ---------------------------------------------------------------------------
# Prometheus HTTP Middleware
# ---------------------------------------------------------------------------

class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """
    FastAPI / Starlette middleware collecting HTTP request counts, durations,
    and concurrent in-flight requests.
    """

    async def dispatch(self, request: Request, call_next):
        method = request.method
        # We start with normalized raw path; will refine with matched route after call_next
        route_label = normalize_route_path(request.url.path)

        try:
            http_requests_in_progress.labels(method=method, route=route_label).inc()
        except Exception:
            pass

        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            # If the router matched a parameterized template, use it for bounded cardinality
            route_label = extract_route_label(request)
            return response
        except Exception:
            route_label = extract_route_label(request)
            status_code = 500
            raise
        finally:
            duration = time.perf_counter() - start_time
            try:
                http_requests_in_progress.labels(method=method, route=route_label).dec()
            except Exception:
                pass

            try:
                status_str = str(status_code)
                http_requests_total.labels(
                    method=method,
                    route=route_label,
                    status_code=status_str,
                ).inc()
                http_request_duration_seconds.labels(
                    method=method,
                    route=route_label,
                    status_code=status_str,
                ).observe(duration)
            except Exception as exc:
                logger.warning("Failed to record HTTP metrics: %s", exc)
