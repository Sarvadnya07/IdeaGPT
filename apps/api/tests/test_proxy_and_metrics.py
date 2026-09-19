"""
IdeaGPT API — Operational Hardening Test Suite (Stage 3)
Verifies:
1. Reverse-Proxy Trusted Topology & Client IP Resolution (V1.1-SHOULD-01)
   - Rejection of header spoofing from untrusted direct peers
   - Safe parsing of X-Forwarded-For and X-Real-IP behind trusted proxies
   - Multi-hop reverse proxy chain resolution (RFC 7239 compliant)
   - Malformed/injection header handling
   - Fail-closed production configuration validation for FORWARDED_ALLOW_IPS="*"
2. Rate Limiting Behaviors across Personas & Network Topologies
   - Authenticated User A vs User B quota isolation
   - Anonymous direct client rate limiting by socket IP
   - Trusted proxy forwarded client rate limiting by resolved IP
   - Untrusted peer spoofing prevention (attacker rotating XFF is constrained by socket IP)
3. Prometheus Operational Metrics (V1.1-SHOULD-02)
   - /metrics returns text/plain; version=0.0.4; charset=utf-8
   - Standard metric families present (http_requests_total, http_request_duration_seconds, etc.)
   - Dynamic AI task gauge reflection
   - AI Gateway request and fallback metrics recording
   - Bounded cardinality: parameterized route templates and normalized UUIDs
   - Strict security: no secrets, no user IDs, no tenant IDs in metric output
   - Authentication enforcement (unauthenticated requests return 401/403)
   - Scraper token authentication support
   - Health endpoints remain untouched and functional JSON
"""

import os
import pytest
from httpx import AsyncClient, ASGITransport
from starlette.requests import Request
import jwt as pyjwt

from app.main import app
from app.core.config import settings, Settings
from app.core.proxy import get_client_ip, is_trusted_proxy, _parse_trusted_networks
from app.core.rate_limit import limiter, rate_limit_key_func
from app.core.metrics import (
    normalize_route_path,
    record_ai_request,
    record_ai_fallback,
    record_ai_tokens,
    update_ai_tasks_gauge,
    get_prometheus_exposition_text,
    metrics_registry,
)

TEST_SECRET = os.environ.get("CLERK_JWT_TEST_SECRET", "test_clerk_jwt_hs256_secret_key_for_testing_only_32b")


def _make_token(sub: str = "test_ops_user_001") -> str:
    payload = {
        "sub": sub,
        "exp": 9999999999,
        "iat": 1000000000,
        "iss": settings.clerk_issuer or "https://clerk.test",
    }
    return pyjwt.encode(payload, TEST_SECRET, algorithm="HS256")


# ===========================================================================
# 1. Reverse-Proxy Trust & Client IP Resolution Tests
# ===========================================================================

def test_trusted_proxy_network_parsing():
    """Verify comma-separated IP and CIDR subnet parsing."""
    nets = _parse_trusted_networks("127.0.0.1, ::1, 10.0.0.0/8, 172.16.0.0/12, malformed_ip, *")
    assert len(nets) == 4
    # Check membership
    assert is_trusted_proxy("127.0.0.1", nets)
    assert is_trusted_proxy("10.50.1.1", nets)
    assert is_trusted_proxy("172.20.0.2", nets)
    assert not is_trusted_proxy("198.51.100.5", nets)
    assert not is_trusted_proxy("invalid_str", nets)


def test_client_ip_untrusted_direct_peer_spoof_rejected():
    """Direct connection from untrusted IP must IGNORE all forwarded headers."""
    scope = {
        "type": "http",
        "client": ("198.51.100.55", 54321),
        "headers": [
            (b"x-forwarded-for", b"203.0.113.195, 1.1.1.1"),
            (b"x-real-ip", b"8.8.8.8"),
        ],
    }
    req = Request(scope)
    # The direct peer 198.51.100.55 is NOT in settings.FORWARDED_ALLOW_IPS (default 127.0.0.1,::1)
    resolved = get_client_ip(req)
    assert resolved == "198.51.100.55"


def test_client_ip_trusted_proxy_single_hop():
    """Connection from trusted proxy (127.0.0.1) parses single-hop client IP."""
    scope = {
        "type": "http",
        "client": ("127.0.0.1", 54321),
        "headers": [
            (b"x-forwarded-for", b"203.0.113.195"),
        ],
    }
    req = Request(scope)
    resolved = get_client_ip(req)
    assert resolved == "203.0.113.195"


def test_client_ip_trusted_proxy_multi_hop_chain():
    """
    Multi-hop proxy chain: client (203.0.113.195) -> proxy1 (10.0.0.2) -> proxy2 (127.0.0.1) -> app.
    When 10.0.0.0/8 and 127.0.0.1 are trusted, extracts leftmost untrusted client IP.
    """
    orig_config = settings.FORWARDED_ALLOW_IPS
    settings.FORWARDED_ALLOW_IPS = "127.0.0.1,::1,10.0.0.0/8"
    try:
        scope = {
            "type": "http",
            "client": ("127.0.0.1", 54321),
            "headers": [
                (b"x-forwarded-for", b"203.0.113.195, 10.0.0.2"),
            ],
        }
        req = Request(scope)
        resolved = get_client_ip(req)
        assert resolved == "203.0.113.195"
    finally:
        settings.FORWARDED_ALLOW_IPS = orig_config


def test_client_ip_trusted_proxy_fallback_to_x_real_ip():
    """Trusted proxy without XFF falls back to valid X-Real-IP."""
    scope = {
        "type": "http",
        "client": ("127.0.0.1", 54321),
        "headers": [
            (b"x-real-ip", b"198.51.100.77"),
        ],
    }
    req = Request(scope)
    resolved = get_client_ip(req)
    assert resolved == "198.51.100.77"


def test_client_ip_malformed_header_fails_safe():
    """Malformed or injection headers safely fall back to direct peer without raising."""
    scope = {
        "type": "http",
        "client": ("127.0.0.1", 54321),
        "headers": [
            (b"x-forwarded-for", b"<script>alert(1)</script>, '; DROP TABLE users; --"),
            (b"x-real-ip", b"not-an-ip"),
        ],
    }
    req = Request(scope)
    resolved = get_client_ip(req)
    assert resolved == "127.0.0.1"


def test_production_config_rejects_wildcard_forwarded_allow_ips():
    """Production mode must fail fast if FORWARDED_ALLOW_IPS is set to '*'."""
    s = Settings(
        _env_file=None,
        APP_ENV="production",
        CLERK_PUBLISHABLE_KEY="pk_test_dGVzdC5jbGVyay5hY2NvdW50cy5kZXYk",
        CLERK_JWT_TEST_SECRET=None,
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        CREDENTIAL_ENCRYPTION_KEY="test_key_32_bytes_long_exact__",
        FORWARDED_ALLOW_IPS="*",
    )
    with pytest.raises(RuntimeError, match=r"FORWARDED_ALLOW_IPS cannot be '\*'"):
        s.validate_production_config()


# ===========================================================================
# 2. Rate Limiting Tests (Personas & Network Topologies)
# ===========================================================================

def test_rate_limit_key_func_authenticated_user_isolation():
    """Authenticated requests key by verified user_id / clerk_id regardless of IP."""
    scope_a = {
        "type": "http",
        "client": ("198.51.100.1", 5000),
        "headers": [],
    }
    req_a = Request(scope_a)
    req_a.state.user_id = "user_uuid_aaa"

    scope_b = {
        "type": "http",
        "client": ("198.51.100.1", 5000),  # Same IP
        "headers": [],
    }
    req_b = Request(scope_b)
    req_b.state.user_id = "user_uuid_bbb"

    assert rate_limit_key_func(req_a) == "user:user_uuid_aaa"
    assert rate_limit_key_func(req_b) == "user:user_uuid_bbb"
    assert rate_limit_key_func(req_a) != rate_limit_key_func(req_b)


def test_rate_limit_key_func_anonymous_trusted_proxy_forwarded():
    """Anonymous request behind trusted proxy keys by resolved client IP."""
    scope = {
        "type": "http",
        "client": ("127.0.0.1", 5000),
        "headers": [(b"x-forwarded-for", b"203.0.113.88")],
    }
    req = Request(scope)
    assert rate_limit_key_func(req) == "ip:203.0.113.88"


def test_rate_limit_key_func_anonymous_untrusted_spoofing_constrained():
    """
    Untrusted direct peer attempting to spoof XFF must be keyed by its direct IP,
    preventing quota rotation abuse.
    """
    scope1 = {
        "type": "http",
        "client": ("198.51.100.99", 5000),
        "headers": [(b"x-forwarded-for", b"1.1.1.1")],
    }
    scope2 = {
        "type": "http",
        "client": ("198.51.100.99", 5000),
        "headers": [(b"x-forwarded-for", b"2.2.2.2")],
    }
    req1 = Request(scope1)
    req2 = Request(scope2)

    assert rate_limit_key_func(req1) == "ip:198.51.100.99"
    assert rate_limit_key_func(req2) == "ip:198.51.100.99"
    # Both are keyed identically so attacker cannot bypass limits
    assert rate_limit_key_func(req1) == rate_limit_key_func(req2)


# ===========================================================================
# 3. Prometheus Metrics Endpoint & Exposition Tests
# ===========================================================================

@pytest.mark.asyncio
async def test_metrics_endpoint_unauthenticated_rejected():
    """Unauthenticated GET /metrics must return HTTP 401 or 403."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/metrics")
        assert res.status_code in [401, 403]


@pytest.mark.asyncio
async def test_metrics_endpoint_authenticated_returns_prometheus_format():
    """Authenticated GET /metrics must return 200 with standard Prometheus text exposition format."""
    auth_header = {"Authorization": f"Bearer {_make_token(sub='test_metrics_ops_user')}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Generate some traffic to exercise middleware
        await client.get("/health/live")
        await client.get("/health/ready")

        res = await client.get("/metrics", headers=auth_header)
        assert res.status_code == 200
        content_type = res.headers.get("content-type", "")
        assert "text/plain" in content_type
        assert "version=0.0.4" in content_type

        body = res.text
        # Check standard Prometheus exposition headers
        assert "# HELP http_requests_total" in body
        assert "# TYPE http_requests_total counter"
        assert "# HELP http_request_duration_seconds" in body
        assert "# TYPE http_request_duration_seconds histogram"
        assert "# HELP http_requests_in_progress" in body

        # Verify no JSON format
        assert not body.strip().startswith("{")
        assert not body.strip().endswith("}")


@pytest.mark.asyncio
async def test_metrics_endpoint_with_scrape_token():
    """Scraper token in METRICS_SCRAPE_TOKEN authorizes Prometheus scrapers."""
    orig_token = settings.METRICS_SCRAPE_TOKEN
    settings.METRICS_SCRAPE_TOKEN = "secret_prometheus_scrape_token_123"
    try:
        scrape_header = {"Authorization": "Bearer secret_prometheus_scrape_token_123"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get("/metrics", headers=scrape_header)
            assert res.status_code == 200
            assert "text/plain" in res.headers.get("content-type", "")
    finally:
        settings.METRICS_SCRAPE_TOKEN = orig_token


def test_metrics_route_normalization_bounded_cardinality():
    """Route normalizer collapses UUIDs and numeric IDs to prevent label dimension explosion."""
    assert normalize_route_path("/api/v1/projects/33a9c950-df55-46c6-8b7d-a020ab808b9d") == "/api/v1/projects/{id}"
    assert normalize_route_path("/api/v1/ideas/999/evaluations/123e4567-e89b-12d3-a456-426614174000") == "/api/v1/ideas/{id}/evaluations/{id}"
    assert normalize_route_path("/health/live?token=secret123") == "/health/live"
    assert normalize_route_path("/") == "/"


def test_metrics_no_secrets_or_user_ids_in_output():
    """Inspect generated Prometheus text to ensure zero secret/tenant/user leakage."""
    # Record mock events
    record_ai_request(provider="mock", operation="test_op", status="success", duration_seconds=0.15)
    record_ai_fallback(primary_provider="openai", fallback_provider="groq")
    record_ai_tokens(provider="mock", prompt_tokens=150, completion_tokens=300)
    update_ai_tasks_gauge({"completed": 5, "pending": 2, "failed": 0})

    text_bytes = get_prometheus_exposition_text()
    text = text_bytes.decode("utf-8")

    # Verify presence of expected metric families
    assert "ideagpt_ai_requests_total" in text
    assert "ideagpt_ai_fallback_total" in text
    assert "ideagpt_ai_tokens_total" in text
    assert "ideagpt_ai_tasks" in text

    # Verify absence of forbidden labels
    forbidden_terms = ["user_id=", "tenant_id=", "idea_id=", "artifact_id=", "task_id=", "prompt=", "secret", "password"]
    for term in forbidden_terms:
        assert term not in text.lower(), f"Forbidden identifier or secret leaked in metrics: {term}"


@pytest.mark.asyncio
async def test_health_endpoints_remain_json_unaltered():
    """Operational health endpoints must continue to return structured JSON without alteration."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res_live = await client.get("/health/live")
        assert res_live.status_code == 200
        assert "application/json" in res_live.headers.get("content-type", "")
        assert res_live.json()["status"] == "live"

        res_ready = await client.get("/health/ready")
        assert res_ready.status_code == 200
        assert "application/json" in res_ready.headers.get("content-type", "")
        assert res_ready.json()["status"] == "ready"
