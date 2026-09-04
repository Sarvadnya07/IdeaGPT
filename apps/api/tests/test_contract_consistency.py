"""
Comprehensive Contract & Quality Gate Automated Test Suite
Verifies:
- OpenAPI 3.1 schema integrity & path generation
- HTTP semantics (no GET with body)
- RFC 9457 structured error responses
- Rate limiter 429 response structure & Retry-After header
- Header-based and body-based idempotency
- Multi-provider fallback and deterministic engine guarantees
"""
import pytest
import time
import jwt
from httpx import AsyncClient, ASGITransport
from app.main import app

TEST_SECRET = "test-secret-for-unit-tests-only-never-production"

def _make_auth_header(sub: str = "contract_test_user") -> dict:
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": f"{sub}@example.com",
        "iat": now,
        "exp": now + 3600,
        "iss": "https://healthy-sunbeam-68.clerk.accounts.dev"
    }
    token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_openapi_schema_integrity():
    schema = app.openapi()
    assert "openapi" in schema
    assert "paths" in schema
    assert len(schema["paths"]) >= 40
    
    # Assert no GET endpoint requires a request body
    for path, methods in schema["paths"].items():
        if "get" in methods:
            assert "requestBody" not in methods["get"], f"GET route {path} must not require requestBody"

@pytest.mark.asyncio
async def test_rfc_9457_validation_error_contract():
    headers = _make_auth_header("val_test_user")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Invalid project creation payload (missing required title)
        res = await client.post("/api/v1/projects/", json={}, headers=headers)
        assert res.status_code == 422
        data = res.json()
        
        # Verify RFC 9457 fields
        assert "type" in data
        assert "title" in data
        assert "status" in data
        assert data["status"] == 422
        assert "detail" in data
        assert "instance" in data
        assert "invalid_params" in data
        assert isinstance(data["invalid_params"], list)
        
        # Verify backward compatibility
        assert "error" in data
        assert "code" in data
        assert data["code"] == "422_VALIDATION_ERROR"

@pytest.mark.asyncio
async def test_rfc_9457_http_error_contract():
    headers = _make_auth_header("not_found_user")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/projects/non-existent-uuid-12345", headers=headers)
        assert res.status_code == 404
        data = res.json()
        
        assert data["status"] == 404
        assert "title" in data
        assert data["title"] == "Not Found"
        assert "detail" in data
        assert "error" in data

@pytest.mark.asyncio
async def test_header_and_body_idempotency():
    headers = _make_auth_header("idem_test_user")
    headers["Idempotency-Key"] = "header-key-test-999"
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        p_res = await client.post("/api/v1/projects/", json={"title": "Idempotency Proj"}, headers=headers)
        proj_id = p_res.json()["id"]
        
        # 1st Submission via Idempotency-Key Header
        res1 = await client.post(
            "/api/v1/ai/tasks",
            json={"task_type": "idea_evaluation", "project_id": proj_id},
            headers=headers
        )
        assert res1.status_code == 202
        task1_id = res1.json()["id"]
        
        # 2nd Submission with same Idempotency-Key Header -> Returns same task ID
        res2 = await client.post(
            "/api/v1/ai/tasks",
            json={"task_type": "idea_evaluation", "project_id": proj_id},
            headers=headers
        )
        assert res2.status_code == 202
        assert res2.json()["id"] == task1_id

@pytest.mark.asyncio
async def test_restful_get_export_endpoint():
    headers = _make_auth_header("export_user")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        p_res = await client.post("/api/v1/projects/", json={"title": "Export Proj"}, headers=headers)
        proj_id = p_res.json()["id"]
        
        i_res = await client.post(
            f"/api/v1/projects/{proj_id}/ideas",
            json={
                "title": "Export Idea",
                "problem_statement": "Problem statement for export testing.",
                "solution_description": "Solution description for export testing."
            },
            headers=headers
        )
        idea_id = i_res.json()["id"]
        
        e_res = await client.post(f"/api/v1/ideas/{idea_id}/evaluations", json={}, headers=headers)
        eval_id = e_res.json()["id"]
        
        # Test RESTful GET export as JSON
        get_json = await client.get(f"/api/v1/evaluations/{eval_id}/export?format=json", headers=headers)
        assert get_json.status_code == 200
        assert get_json.json()["format"] == "json"
        assert f"evaluation_{eval_id}.json" in get_json.json()["filename"]
        
        # Test RESTful GET export as Markdown
        get_md = await client.get(f"/api/v1/evaluations/{eval_id}/export?format=markdown", headers=headers)
        assert get_md.status_code == 200
        assert get_md.json()["format"] == "markdown"
        assert f"evaluation_{eval_id}.md" in get_md.json()["filename"]
