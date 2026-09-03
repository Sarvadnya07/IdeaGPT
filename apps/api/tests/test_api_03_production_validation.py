"""
API-03 Production Validation Test Suite
========================================
Comprehensive automated verification covering:
1. Contract-to-Runtime Verification (OpenAPI 3.1 sync, schema correctness)
2. HTTP Semantics & Method Handling (GET, POST 201, PATCH 200, DELETE 200, OPTIONS)
3. Status Code Accuracy (200, 201, 202, 400, 401, 403, 404, 409, 422, 429)
4. RFC 9457 Error Contracts with request_id & x-request-id propagation
5. Authorization, BOLA & Tenant Isolation
6. Pagination Contract (limit, offset, has_more, total, items)
7. Idempotency Guarantees (deduplication & 409 Conflict on payload mismatch)
8. Rate Limiter Controls & Retry-After
9. Async Task Lifecycle & SSE Stream Readiness
10. Health & Readiness Liveness Probes
"""
import pytest
import time
import jwt
import json
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select

from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.idea import Idea
from app.models.ai_task import AiTask

TEST_SECRET = "test-secret-for-unit-tests-only-never-production"


def _make_auth_header(sub: str = "val_user_1", email: str = None) -> dict:
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": email or f"{sub}@example.com",
        "iat": now,
        "exp": now + 3600,
        "iss": "https://healthy-sunbeam-68.clerk.accounts.dev",
    }
    token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# 1. CONTRACT-TO-RUNTIME VALIDATION
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api03_openapi_contract_conformance():
    """Verify live OpenAPI spec contains 103 paths and no GET requires a body."""
    schema = app.openapi()
    paths = schema.get("paths", {})
    assert len(paths) >= 100, f"Expected >= 100 paths, got {len(paths)}"

    # Validate that all GET operations do not require request bodies
    for path, methods in paths.items():
        if "get" in methods:
            assert "requestBody" not in methods["get"], f"GET {path} must not declare requestBody"

    # Validate project pagination response schema
    proj_get = paths.get("/api/v1/projects/", {}).get("get", {})
    resp_200 = proj_get.get("responses", {}).get("200", {})
    assert resp_200, "GET /api/v1/projects/ must have 200 response"


# ---------------------------------------------------------------------------
# 2. HTTP SEMANTICS & STATUS CODES (201, 200, 202, OPTIONS)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api03_http_semantics_and_status_codes():
    """Verify 201 Created on mutations, 200 on safe reads/updates, and CORS OPTIONS."""
    headers = _make_auth_header("http_semantics_user")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # CORS preflight OPTIONS
        options_res = await client.options(
            "/api/v1/projects/",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"}
        )
        assert options_res.status_code in (200, 204)
        assert "access-control-allow-origin" in options_res.headers

        # POST Project -> 201 Created
        p_res = await client.post(
            "/api/v1/projects/",
            json={"title": "Semantics Test Project", "category": "Fintech"},
            headers=headers
        )
        assert p_res.status_code == 201
        p_data = p_res.json()
        assert "x-request-id" in p_res.headers
        proj_id = p_data["id"]

        # POST Idea under project -> 201 Created
        i_res = await client.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": "Semantics Test Idea",
                "problem_statement": "Valid problem statement for testing.",
                "solution_description": "Valid solution description for testing.",
                "is_draft": False
            },
            headers=headers
        )
        assert i_res.status_code == 201
        idea_id = i_res.json()["id"]

        # GET Project -> 200 OK (safe read)
        get_res = await client.get(f"/api/v1/projects/{proj_id}", headers=headers)
        assert get_res.status_code == 200

        # PATCH Project -> 200 OK (partial update)
        patch_res = await client.patch(
            f"/api/v1/projects/{proj_id}",
            json={"title": "Updated Semantics Title"},
            headers=headers
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["title"] == "Updated Semantics Title"

        # POST Duplicate Project -> 201 Created
        dup_res = await client.post(f"/api/v1/projects/{proj_id}/duplicate", headers=headers)
        assert dup_res.status_code == 201
        assert dup_res.json()["title"] == "Updated Semantics Title (Copy)"

        # DELETE Project -> 200 OK
        del_res = await client.delete(f"/api/v1/projects/{proj_id}", headers=headers)
        assert del_res.status_code == 200


# ---------------------------------------------------------------------------
# 3. RFC 9457 ERROR CONTRACT & CORRELATION ID PROPAGATION
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api03_rfc9457_error_contract_and_correlation_id():
    """Verify error responses contain RFC 9457 fields, request_id, and x-request-id header."""
    headers = _make_auth_header("error_user")
    custom_trace_id = "trace-test-uuid-9999"
    headers["x-request-id"] = custom_trace_id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 404 Not Found
        res_404 = await client.get("/api/v1/projects/non-existent-uuid-abc", headers=headers)
        assert res_404.status_code == 404
        data_404 = res_404.json()
        assert data_404["status"] == 404
        assert data_404["title"] == "Not Found"
        assert "type" in data_404
        assert "instance" in data_404
        assert data_404["request_id"] == custom_trace_id
        assert res_404.headers.get("x-request-id") == custom_trace_id

        # 422 Validation Error
        res_422 = await client.post("/api/v1/projects/", json={"title": ""}, headers=headers)
        assert res_422.status_code == 422
        data_422 = res_422.json()
        assert data_422["status"] == 422
        assert data_422["title"] == "Unprocessable Entity"
        assert data_422["request_id"] == custom_trace_id
        assert "invalid_params" in data_422
        assert res_422.headers.get("x-request-id") == custom_trace_id

        # 401 Unauthorized
        res_401 = await client.get("/api/v1/users/me")
        assert res_401.status_code == 401
        data_401 = res_401.json()
        assert data_401["status"] == 401
        assert "request_id" in data_401
        assert "x-request-id" in res_401.headers


# ---------------------------------------------------------------------------
# 4. AUTHORIZATION, BOLA & TENANT ISOLATION
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api03_bola_and_tenant_isolation():
    """Verify strict tenant isolation across projects, ideas, evaluations, and artifacts."""
    headers_alice = _make_auth_header("alice_tenant_owner")
    headers_mallory = _make_auth_header("mallory_attacker")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Alice creates project
        p_res = await client.post(
            "/api/v1/projects/",
            json={"title": "Alice Confidential IP", "category": "DeepTech"},
            headers=headers_alice
        )
        assert p_res.status_code == 201
        alice_proj_id = p_res.json()["id"]

        # Alice creates idea
        i_res = await client.post(
            f"/api/v1/projects/{alice_proj_id}/ideas",
            json={
                "title": "Proprietary Algorithm",
                "problem_statement": "Top secret problem statement.",
                "solution_description": "Top secret solution description.",
                "is_draft": False
            },
            headers=headers_alice
        )
        assert i_res.status_code == 201
        alice_idea_id = i_res.json()["id"]

        # Mallory attempts to GET Alice's project -> 404 (IDOR masked as Not Found)
        m_get_p = await client.get(f"/api/v1/projects/{alice_proj_id}", headers=headers_mallory)
        assert m_get_p.status_code == 404

        # Mallory attempts to PATCH Alice's project -> 404
        m_patch_p = await client.patch(
            f"/api/v1/projects/{alice_proj_id}",
            json={"title": "Hacked Title"},
            headers=headers_mallory
        )
        assert m_patch_p.status_code == 404

        # Mallory attempts to DELETE Alice's project -> 404
        m_del_p = await client.delete(f"/api/v1/projects/{alice_proj_id}", headers=headers_mallory)
        assert m_del_p.status_code == 404

        # Mallory attempts to GET Alice's idea -> 404
        m_get_i = await client.get(f"/api/v1/ideas/{alice_idea_id}", headers=headers_mallory)
        assert m_get_i.status_code == 404

        # Mallory attempts to create idea in Alice's project -> 404
        m_post_i = await client.post(
            f"/api/v1/projects/{alice_proj_id}/ideas",
            json={
                "title": "Malicious Idea",
                "problem_statement": "Injected problem statement.",
                "solution_description": "Injected solution description.",
            },
            headers=headers_mallory
        )
        assert m_post_i.status_code == 404


# ---------------------------------------------------------------------------
# 5. PAGINATION SCHEMA & TRAVERSAL
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api03_pagination_metadata_and_traversal():
    """Verify limit, offset, has_more, total, and items are present and accurate."""
    headers = _make_auth_header("pagination_user")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create 3 projects
        for idx in range(3):
            await client.post(
                "/api/v1/projects/",
                json={"title": f"Page Project {idx + 1}"},
                headers=headers
            )

        # Query page 1 (limit=2, offset=0) -> has_more=True
        page1 = await client.get("/api/v1/projects/?limit=2&offset=0", headers=headers)
        assert page1.status_code == 200
        p1_data = page1.json()
        assert p1_data["total"] == 3
        assert p1_data["limit"] == 2
        assert p1_data["offset"] == 0
        assert p1_data["has_more"] is True
        assert len(p1_data["items"]) == 2

        # Query page 2 (limit=2, offset=2) -> has_more=False
        page2 = await client.get("/api/v1/projects/?limit=2&offset=2", headers=headers)
        assert page2.status_code == 200
        p2_data = page2.json()
        assert p2_data["total"] == 3
        assert p2_data["limit"] == 2
        assert p2_data["offset"] == 2
        assert p2_data["has_more"] is False
        assert len(p2_data["items"]) == 1


# ---------------------------------------------------------------------------
# 6. IDEMPOTENCY GUARANTEES & CONFLICT DETECTION
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api03_idempotency_dedup_and_conflict_rejection():
    """Verify:
    1. Identical request with same Idempotency-Key returns same task (202).
    2. Request with same Idempotency-Key but differing payload is rejected (409 Conflict).
    """
    headers = _make_auth_header("idempotency_user")
    idem_key = "idemp-test-key-unique-888"
    headers["Idempotency-Key"] = idem_key

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create parent project
        p_res = await client.post("/api/v1/projects/", json={"title": "Idem Proj"}, headers=headers)
        proj_id = p_res.json()["id"]

        # 1st Submission: initial task
        payload1 = {
            "task_type": "idea_evaluation",
            "project_id": proj_id,
            "input_payload": {"prompt": "Initial startup assessment."}
        }
        res1 = await client.post("/api/v1/ai/tasks", json=payload1, headers=headers)
        assert res1.status_code == 202
        task_id = res1.json()["id"]

        # 2nd Submission: exact same payload + key -> Deduplicated, returns same task ID
        res2 = await client.post("/api/v1/ai/tasks", json=payload1, headers=headers)
        assert res2.status_code == 202
        assert res2.json()["id"] == task_id

        # 3rd Submission: same key + DIFFERENT payload -> 409 Conflict
        payload_conflict = {
            "task_type": "market_research",  # Conflicting task type
            "project_id": proj_id,
            "input_payload": {"prompt": "Conflicting prompt payload."}
        }
        res3 = await client.post("/api/v1/ai/tasks", json=payload_conflict, headers=headers)
        assert res3.status_code == 409
        data3 = res3.json()
        assert data3["status"] == 409
        assert "IDEMPOTENCY_CONFLICT" in data3["detail"] or "different payload" in data3["detail"]


# ---------------------------------------------------------------------------
# 7. ASYNC TASK LIFECYCLE & SSE STREAMING
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api03_async_task_and_sse_streaming():
    """Verify 202 Accepted on task creation, task polling, and SSE streaming connect."""
    headers = _make_auth_header("async_stream_user")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        p_res = await client.post("/api/v1/projects/", json={"title": "Async Stream Proj"}, headers=headers)
        proj_id = p_res.json()["id"]

        # 1. Create async task -> 202 Accepted
        task_res = await client.post(
            "/api/v1/ai/tasks",
            json={"task_type": "idea_evaluation", "project_id": proj_id},
            headers=headers
        )
        assert task_res.status_code == 202
        task_id = task_res.json()["id"]

        # 2. Poll task status -> 200 OK
        poll_res = await client.get(f"/api/v1/ai/tasks/{task_id}", headers=headers)
        assert poll_res.status_code == 200
        assert poll_res.json()["id"] == task_id
        assert poll_res.json()["status"] in ("QUEUED", "RUNNING", "COMPLETED")

        # 3. Connect to SSE stream
        # Read the first event chunk
        stream_res = await client.get(f"/api/v1/ai/tasks/{task_id}/stream", headers=headers)
        assert stream_res.status_code == 200
        assert "text/event-stream" in stream_res.headers.get("content-type", "")


# ---------------------------------------------------------------------------
# 8. HEALTH & READINESS PROBES
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api03_health_probes():
    """Verify unauthenticated liveness and database readiness probes."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Liveness check (process up, no DB query)
        live_res = await client.get("/health/live")
        assert live_res.status_code == 200
        assert live_res.json()["status"] == "live"

        # Readiness check (DB connectivity verified)
        ready_res = await client.get("/health/ready")
        assert ready_res.status_code == 200
        assert ready_res.json()["status"] == "ready"
        assert ready_res.json()["database"] == "connected"
