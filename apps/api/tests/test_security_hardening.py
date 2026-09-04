import pytest
import time
import uuid
import jwt
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.core.logging import sanitize_request_id
from app.models.user import User
from app.models.project import Project
from app.models.idea import Idea
from app.models.ai_task import AiTask
from app.services.ai_task_service import AiTaskService

def make_test_token(clerk_id: str, email: str = "test@example.com", expires_in: int = 3600) -> str:
    payload = {
        "sub": clerk_id,
        "email": email,
        "iss": settings.clerk_issuer or "https://clerk.ideagpt.dev",
        "exp": int(time.time()) + expires_in,
        "iat": int(time.time()),
    }
    secret = settings.CLERK_JWT_TEST_SECRET or "prod-baseline-test-secret-32-chars-long!"
    return jwt.encode(payload, secret, algorithm="HS256")

# ---------------------------------------------------------------------------
# PHASE 1 & 2: Mass Assignment Privilege Escalation Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_users_cannot_escalate_role_via_patch_me():
    """Verify that attempting to escalate role to admin via PATCH /api/v1/users/me is strictly rejected."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token = make_test_token("user_mass_assign_test_1", "user1@example.com")

        # First get or create user profile
        res_me = await ac.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        assert res_me.status_code == 200
        assert res_me.json()["role"] == "user"

        # Attempt to patch role: admin
        res_patch = await ac.patch(
            "/api/v1/users/me",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {token}"}
        )
        # Should be rejected with 422 Unprocessable Entity due to extra="forbid"
        assert res_patch.status_code == 422

        # Verify role was not modified in database
        res_verify = await ac.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        assert res_verify.json()["role"] == "user"

@pytest.mark.anyio
async def test_users_cannot_modify_sensitive_fields_via_patch_me():
    """Verify that attempting to modify id, clerk_id, is_admin, or permissions is rejected with 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token = make_test_token("user_mass_assign_test_2", "user2@example.com")

        for bad_payload in [
            {"clerk_id": "user_hijacked_999"},
            {"id": 99999},
            {"is_admin": True},
            {"permissions": ["*"]},
        ]:
            res = await ac.patch(
                "/api/v1/users/me",
                json=bad_payload,
                headers={"Authorization": f"Bearer {token}"}
            )
            assert res.status_code == 422

@pytest.mark.anyio
async def test_users_can_update_permitted_profile_fields():
    """Verify legitimate updates to allowed profile fields succeed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token = make_test_token("user_legit_update_test", "legit@example.com")

        res_patch = await ac.patch(
            "/api/v1/users/me",
            json={
                "name": "Sarah Connor",
                "username": "sarah_c",
                "timezone": "America/Los_Angeles",
                "locale": "en-US",
                "onboarding_completed": True
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res_patch.status_code == 200
        data = res_patch.json()
        assert data["name"] == "Sarah Connor"
        assert data["username"] == "sarah_c"
        assert data["timezone"] == "America/Los_Angeles"
        assert data["onboarding_completed"] is True

# ---------------------------------------------------------------------------
# PHASE 17: Request ID Sanitization & Hardening Tests
# ---------------------------------------------------------------------------

def test_sanitize_request_id_unit():
    """Unit test request ID sanitization logic."""
    # 1. Normal UUID
    valid_uuid = "e7b0a708-3011-4a4b-9e45-1c88d8b67104"
    assert sanitize_request_id(valid_uuid) == valid_uuid

    # 2. None / Empty
    empty_result = sanitize_request_id(None)
    assert uuid.UUID(empty_result) is not None

    # 3. Garbage / Non-UUID string
    garbage_result = sanitize_request_id("arbitrary-script-injection<script>")
    assert garbage_result != "arbitrary-script-injection<script>"
    assert uuid.UUID(garbage_result) is not None

    # 4. Newline Injection
    newline_result = sanitize_request_id("e7b0a708-3011-4a4b-9e45-1c88d8b67104\nINJECTED_LOG_ENTRY")
    assert newline_result != "e7b0a708-3011-4a4b-9e45-1c88d8b67104\nINJECTED_LOG_ENTRY"
    assert "\n" not in newline_result
    assert uuid.UUID(newline_result) is not None

    # 5. Oversized Header
    oversized_result = sanitize_request_id("a" * 1000)
    assert len(oversized_result) == 36
    assert uuid.UUID(oversized_result) is not None

@pytest.mark.anyio
async def test_request_logging_middleware_replaces_malicious_request_id():
    """Integration test verifying middleware sanitizes malicious x-request-id in HTTP responses."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/health/live",
            headers={"x-request-id": "malicious\r\ninjected_log<script>"}
        )
        assert res.status_code == 200
        returned_id = res.headers.get("x-request-id")
        assert returned_id is not None
        assert "malicious" not in returned_id
        assert "\n" not in returned_id
        assert uuid.UUID(returned_id) is not None

# ---------------------------------------------------------------------------
# PHASE 15 & 16: Operational Endpoints Authentication & Sanitization
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_operational_endpoints_require_authentication():
    """Verify that operational and configuration endpoints reject unauthenticated access with 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # /health/config must require auth
        res_cfg = await ac.get("/health/config")
        assert res_cfg.status_code == 401

        # /health/ai must require auth
        res_ai = await ac.get("/health/ai")
        assert res_ai.status_code == 401

        # /health/providers must require auth
        res_prov = await ac.get("/health/providers")
        assert res_prov.status_code == 401

        # /metrics must require auth
        res_met = await ac.get("/metrics")
        assert res_met.status_code == 401

        # /api/v1/ai/registry/refresh must require auth
        res_ref = await ac.post("/api/v1/ai/registry/refresh")
        assert res_ref.status_code == 401

@pytest.mark.anyio
async def test_operational_endpoints_accessible_with_valid_token():
    """Verify authenticated user can access operational endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token = make_test_token("user_ops_test", "ops@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        res_cfg = await ac.get("/health/config", headers=headers)
        assert res_cfg.status_code == 200

        res_ai = await ac.get("/health/ai", headers=headers)
        assert res_ai.status_code == 200

        res_prov = await ac.get("/health/providers", headers=headers)
        assert res_prov.status_code == 200

        res_met = await ac.get("/metrics", headers=headers)
        assert res_met.status_code == 200

# ---------------------------------------------------------------------------
# PHASE 18: Search Wildcard Escaping Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_project_search_escapes_wildcards():
    """Verify that searching for '%' or '_' does not perform SQL wildcard expansion."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token = make_test_token("user_search_wildcard_test", "search@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        # Create project with 100% Growth
        await ac.post(
            "/api/v1/projects/",
            json={"title": "100% Growth Startup", "category": "Fintech"},
            headers=headers
        )
        # Create normal project
        await ac.post(
            "/api/v1/projects/",
            json={"title": "Ordinary Project", "category": "Fintech"},
            headers=headers
        )

        # Search for "%" should only match "100% Growth Startup"
        res_search = await ac.get("/api/v1/projects/?search=%", headers=headers)
        assert res_search.status_code == 200
        items = res_search.json().get("items", [])
        assert len(items) == 1
        assert items[0]["title"] == "100% Growth Startup"

# ---------------------------------------------------------------------------
# PHASE 4 & 26: Cross-Tenant Isolation (IDOR)
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_cross_tenant_project_isolation():
    """Verify User B cannot view, modify, or delete User A's project."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token_a = make_test_token("user_tenant_owner_a", "ownera@example.com")
        token_b = make_test_token("user_tenant_attacker_b", "attackerb@example.com")

        # User A creates a project
        res_create = await ac.post(
            "/api/v1/projects/",
            json={"title": "Confidential IP Project", "category": "DeepTech"},
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert res_create.status_code == 201
        project_id = res_create.json()["id"]

        # User B attempts to access
        res_get = await ac.get(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert res_get.status_code == 404

        res_patch = await ac.patch(
            f"/api/v1/projects/{project_id}",
            json={"title": "Compromised Project Title"},
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert res_patch.status_code == 404

        res_del = await ac.delete(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert res_del.status_code == 404
