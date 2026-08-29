import pytest
import time
import uuid
import jwt
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.ai.orchestrator.orchestrator import AIOrchestrator
from app.ai.orchestrator.router import AIRouter
from app.ai.exceptions.ai_exceptions import AIInvalidModelException

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

@pytest.mark.anyio
async def test_phase1_cryptography_and_pyjwt():
    import cryptography
    import jwt as pyjwt
    assert cryptography.__version__ is not None
    assert pyjwt.__version__ is not None

@pytest.mark.anyio
async def test_phase2_clerk_config_sanitization():
    status = settings.get_config_status()
    assert "CLERK_PUBLISHABLE_KEY" in status
    assert "CLERK_JWT_ISSUER" in status
    assert "sk_" not in str(status)

@pytest.mark.anyio
async def test_phase4_multi_tenant_isolation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token_a = make_test_token("user_tenant_a_123", "usera@example.com")
        token_b = make_test_token("user_tenant_b_456", "userb@example.com")

        # User A creates a project
        res_create = await ac.post(
            "/api/v1/projects/",
            json={"title": "Project Alpha", "category": "Fintech"},
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert res_create.status_code == 200
        project_a_id = res_create.json()["id"]

        # User B attempts to GET User A's project -> 404
        res_get_b = await ac.get(
            f"/api/v1/projects/{project_a_id}",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert res_get_b.status_code == 404

        # User B attempts to PATCH User A's project -> 404
        res_patch_b = await ac.patch(
            f"/api/v1/projects/{project_a_id}",
            json={"title": "Hacked Title"},
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert res_patch_b.status_code == 404

        # User B attempts to DELETE User A's project -> 404
        res_del_b = await ac.delete(
            f"/api/v1/projects/{project_a_id}",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert res_del_b.status_code == 404

@pytest.mark.anyio
async def test_phase5_and_6_groq_inference_and_orchestrator():
    decision = AIRouter.route_task(task_type="idea_evaluation", requested_provider="auto", requested_model="auto")
    assert "actual_provider" in decision
    assert "actual_model" in decision

    milestones = await AIOrchestrator.generate_roadmap_ai(
        title="Automated Medical Scribe",
        category="Healthtech",
        problem_statement="Doctors spend 3 hours daily writing EHR notes.",
        solution_description="AI ambient voice listener that generates structured SOAP notes.",
        target_users="Physicians and Hospitalists",
        provider="mock"
    )
    assert len(milestones) >= 1
    assert "tasks" in milestones[0]

@pytest.mark.anyio
async def test_phase7_groq_incompatible_model_rejection():
    with pytest.raises(AIInvalidModelException):
        AIRouter.route_task(
            task_type="idea_evaluation",
            requested_provider="groq",
            requested_model="whisper-large-v3"
        )

@pytest.mark.anyio
async def test_phase16_observability_endpoints():
    from tests.test_auth import _make_token
    auth_header = {"Authorization": f"Bearer {_make_token(sub='test_ops_user')}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_live = await ac.get("/health/live")
        assert res_live.status_code == 200
        assert res_live.json()["status"] == "live"

        res_ready = await ac.get("/health/ready")
        assert res_ready.status_code == 200
        assert res_ready.json()["status"] == "ready"

        res_providers = await ac.get("/health/providers", headers=auth_header)
        assert res_providers.status_code == 200
        assert "mock" in res_providers.json()

        res_metrics = await ac.get("/metrics", headers=auth_header)
        assert res_metrics.status_code == 200
        assert "service" in res_metrics.json()


@pytest.mark.anyio
async def test_phase51_production_configuration_safety():
    """Verify that insecure production settings fail fast with RuntimeError."""
    from app.core.config import Settings

    # 1. Missing Clerk issuer in production fails
    prod_bad_clerk = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        CORS_ORIGINS="https://ideagpt.dev",
        CLERK_PUBLISHABLE_KEY=None,
        CLERK_JWT_ISSUER=None,
        CLERK_JWT_TEST_SECRET=None,
    )
    with pytest.raises(RuntimeError, match="CLERK_PUBLISHABLE_KEY or CLERK_JWT_ISSUER must be configured"):
        prod_bad_clerk.validate_production_config()

    # 2. SQLite in production fails
    prod_bad_db = Settings(
        APP_ENV="production",
        DATABASE_URL="sqlite+aiosqlite:///./ideagpt.db",
        CORS_ORIGINS="https://ideagpt.dev",
        CLERK_JWT_ISSUER="https://clerk.ideagpt.dev",
        CLERK_JWT_TEST_SECRET=None,
    )
    with pytest.raises(RuntimeError, match="SQLite DATABASE_URL cannot be used in production"):
        prod_bad_db.validate_production_config()

    # 3. Wildcard CORS in production fails
    prod_bad_cors = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        CORS_ORIGINS="*",
        CLERK_JWT_ISSUER="https://clerk.ideagpt.dev",
        CLERK_JWT_TEST_SECRET=None,
    )
    with pytest.raises(RuntimeError, match="CORS_ORIGINS cannot contain wildcard"):
        prod_bad_cors.validate_production_config()

    # 4. Test JWT Secret in production fails
    prod_bad_secret = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        CORS_ORIGINS="https://ideagpt.dev",
        CLERK_JWT_ISSUER="https://clerk.ideagpt.dev",
        CLERK_JWT_TEST_SECRET="some-test-secret",
    )
    with pytest.raises(RuntimeError, match="CLERK_JWT_TEST_SECRET must NOT be set in production"):
        prod_bad_secret.validate_production_config()

    # 5. Valid production configuration succeeds
    prod_valid = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        CORS_ORIGINS="https://ideagpt.dev,https://app.ideagpt.dev",
        CLERK_JWT_ISSUER="https://clerk.ideagpt.dev",
        CLERK_JWT_TEST_SECRET=None,
    )
    # Should not raise
    prod_valid.validate_production_config()


@pytest.mark.anyio
async def test_database_url_normalization_matrix():
    """Verify Phase 15 Database URL normalization matrix across async app and sync alembic."""
    from app.core.config import Settings

    # CASE A: postgresql+asyncpg:// -> preserved for app
    s_a = Settings(DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db")
    assert s_a.async_database_url.startswith("postgresql+asyncpg://")
    assert s_a.sync_database_url.startswith("postgresql+psycopg2://")

    # CASE B: plain postgresql:// -> normalized to asyncpg for app, psycopg2 for sync
    s_b = Settings(DATABASE_URL="postgresql://user:pass@aws-0.pooler.supabase.com:5432/postgres?sslmode=require")
    assert s_b.async_database_url.startswith("postgresql+asyncpg://")
    assert "sslmode=require" in s_b.async_database_url
    assert s_b.sync_database_url.startswith("postgresql+psycopg2://")
    assert "sslmode=require" in s_b.sync_database_url

    # CASE C: postgresql+psycopg2:// -> converted to asyncpg for app
    s_c = Settings(DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/db")
    assert s_c.async_database_url.startswith("postgresql+asyncpg://")
    assert s_c.sync_database_url.startswith("postgresql+psycopg2://")

    # CASE D: sqlite in development -> accepted
    s_d = Settings(APP_ENV="development", DATABASE_URL="sqlite+aiosqlite:///./ideagpt.db")
    assert s_d.async_database_url.startswith("sqlite+aiosqlite://")
    assert s_d.sync_database_url.startswith("sqlite://")

    # CASE E: sqlite in production -> rejected by validate_production_config
    s_e = Settings(
        APP_ENV="production",
        DATABASE_URL="sqlite+aiosqlite:///./ideagpt.db",
        CLERK_JWT_ISSUER="https://clerk.ideagpt.dev",
        CLERK_JWT_TEST_SECRET=None,
    )
    with pytest.raises(RuntimeError, match="SQLite DATABASE_URL cannot be used in production"):
        s_e.validate_production_config()

    # CASE F: URL with percent-encoded special characters
    s_f = Settings(DATABASE_URL="postgresql://postgres.user:pass%40123@aws-0.supabase.com:5432/postgres")
    assert s_f.async_database_url.startswith("postgresql+asyncpg://")
    assert "%40" in s_f.async_database_url
    assert s_f.sync_database_url.startswith("postgresql+psycopg2://")
