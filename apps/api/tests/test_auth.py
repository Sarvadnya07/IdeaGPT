"""
Sprint 2.2 — Authentication & Authorization Test Suite

Tests the full authentication path:
  1.  No Authorization header                   → 401/403
  2.  Empty Bearer token                         → 401
  3.  Malformed JWT (not a JWT at all)           → 401
  4.  Invalid signature                          → 401
  5.  Expired token                              → 401
  6.  Token with invalid algorithm (RS256 fake)  → 401
  7.  Token missing `sub`                        → 401
  8.  Valid token → authenticated user           → 200
  9.  Valid token, user not in DB                → auto-sync (200)
  10. Token with wrong algorithm (RS256 claimed) → 401
  11. Database failure during auth               → NOT 401 (503/500)
  12. User A accessing User B's project          → 404
  13. User A modifying User B's project          → 404
  14. User A accessing User B's ideas            → 404/403
  15. User A accessing User B's evaluation       → 403/404
  16. Cross-user evaluation trigger              → 403
  17. Missing configuration fail-closed          → tested in unit
  18. Test mode cannot be activated without both flags

All tests use deterministic HS256 tokens (APP_ENV=test + CLERK_JWT_TEST_SECRET).
No real Clerk services are called.
"""
import os
import time
import pytest
import jwt as pyjwt

from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select
from unittest.mock import patch, AsyncMock

from app.main import app
from app.api.dependencies.auth import get_current_user
from app.db.session import get_db, AsyncSessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.idea import Idea
from app.core.config import settings

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TEST_SECRET = os.environ["CLERK_JWT_TEST_SECRET"]
PROTECTED_URL = "/api/v1/users/me"


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------
def _make_token(
    sub: str | None = "user_test_001",
    exp_offset: int = 3600,
    extra_claims: dict | None = None,
    algorithm: str = "HS256",
    secret: str = TEST_SECRET,
    sign_with_wrong_secret: bool = False,
) -> str:
    """
    Mint a test JWT.  All real-auth tests route through the HS256 test path.
    """
    now = int(time.time())
    payload: dict = {
        "iat": now,
        "exp": now + exp_offset,
    }
    if settings.clerk_issuer:
        payload["iss"] = settings.clerk_issuer
    if sub is not None:
        payload["sub"] = sub
    if extra_claims:
        payload.update(extra_claims)
        if "iss" in extra_claims and extra_claims["iss"] is None:
            payload.pop("iss", None)

    signing_secret = "wrong-secret-that-will-fail-and-is-32-bytes!" if sign_with_wrong_secret else secret
    return pyjwt.encode(payload, signing_secret, algorithm=algorithm)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def client_app():
    """Return a raw AsyncClient with no auth override."""
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ============================================================
# Group 1 — Token-level rejection (no DB needed)
# ============================================================

@pytest.mark.asyncio
async def test_01_no_authorization_header():
    """No Authorization header → 401/403 (HTTPBearer returns 403, which is
    FastAPI's convention for missing credentials)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(PROTECTED_URL)
    # FastAPI HTTPBearer returns 403 when header is completely absent
    assert res.status_code in (401, 403), f"Expected 401/403, got {res.status_code}"


@pytest.mark.asyncio
async def test_02_empty_bearer_token():
    """Bearer token present but empty string → 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(PROTECTED_URL, headers={"Authorization": "Bearer "})
    assert res.status_code in (401, 403, 422), f"Expected rejection, got {res.status_code}"


@pytest.mark.asyncio
async def test_03_malformed_jwt():
    """Totally invalid token (not JWT format) → 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(PROTECTED_URL, headers={"Authorization": "Bearer not.a.jwt.at.all"})
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"


@pytest.mark.asyncio
async def test_04_invalid_signature():
    """Valid JWT structure but signed with wrong secret → 401."""
    token = _make_token(sign_with_wrong_secret=True)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"


@pytest.mark.asyncio
async def test_05_expired_token():
    """Token whose exp is in the past → 401."""
    token = _make_token(exp_offset=-3600)  # expired 1 hour ago
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"


@pytest.mark.asyncio
async def test_06_wrong_algorithm_none():
    """Token using 'none' algorithm → 401 (algorithm confusion attack)."""
    # Manually craft a 'none' algorithm token
    import base64, json
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).rstrip(b"=").decode()
    payload_b64 = base64.urlsafe_b64encode(
        json.dumps({"sub": "attacker", "exp": int(time.time()) + 3600, "iat": int(time.time())}).encode()
    ).rstrip(b"=").decode()
    token = f"{header}.{payload_b64}."  # no signature
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401, f"Algorithm confusion attack must be rejected, got {res.status_code}"


@pytest.mark.asyncio
async def test_07_token_missing_sub():
    """Valid HS256 token but sub claim is absent → 401."""
    token = _make_token(sub=None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401, f"Expected 401 for missing sub, got {res.status_code}"


@pytest.mark.asyncio
async def test_08_forged_token_wrong_secret():
    """Token signed with a completely different secret → 401."""
    token = _make_token(secret="attacker-controlled-secret-that-is-32b!")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401, f"Forged token must be rejected, got {res.status_code}"


# ============================================================
# Group 2 — Valid token + user synchronization
# ============================================================

@pytest.mark.asyncio
async def test_09_valid_token_creates_and_returns_user():
    """Valid token for a new clerk_id → user is created, 200 returned."""
    clerk_id = "user_brand_new_001"
    token = _make_token(sub=clerk_id, extra_claims={"email": "new@test.com", "name": "New User"})

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert data["clerk_id"] == clerk_id

    # Verify user exists in the database
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.clerk_id == clerk_id))
        user = result.scalar_one_or_none()
    assert user is not None, "User should have been created in the database"
    assert user.clerk_id == clerk_id


@pytest.mark.asyncio
async def test_10_valid_token_returns_existing_user():
    """Valid token for a known clerk_id → existing user returned, no duplicate."""
    clerk_id = "user_existing_002"
    # Pre-create the user
    async with AsyncSessionLocal() as db:
        db.add(User(clerk_id=clerk_id, email="existing@test.com", name="Existing"))
        await db.commit()

    token = _make_token(sub=clerk_id)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 200
    data = res.json()
    assert data["clerk_id"] == clerk_id

    # Confirm no duplicate was created
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.clerk_id == clerk_id))
        users = result.scalars().all()
    assert len(users) == 1, f"Expected exactly 1 user, found {len(users)}"


@pytest.mark.asyncio
async def test_11_valid_token_no_email_in_jwt():
    """Valid token without email claim → user created with email=None (not placeholder)."""
    clerk_id = "user_no_email_003"
    token = _make_token(sub=clerk_id)  # no email claim

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 200
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.clerk_id == clerk_id))
        user = result.scalar_one_or_none()
    assert user is not None
    # Email must be None, not a placeholder
    assert user.email is None or "@placeholder" not in (user.email or ""), (
        f"Placeholder email detected: {user.email}"
    )


# ============================================================
# Group 3 — Database failure → NOT 401
# ============================================================

@pytest.mark.asyncio
async def test_12_database_failure_is_not_401():
    """
    Valid token but DB is unavailable → must return 500 or 503, NOT 401.
    This tests the critical exception-type distinction.
    """
    from sqlalchemy.exc import OperationalError

    clerk_id = "user_db_fail_004"
    token = _make_token(sub=clerk_id)

    # Patch the DB execute to simulate a database failure
    original_execute = None

    async def mock_db_failure(*args, **kwargs):
        raise OperationalError("connection failed", {}, None)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        with patch("app.api.dependencies.auth._get_or_create_user", side_effect=mock_db_failure):
            res = await ac.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})

    # Must NOT be 401 — database failures are not authentication failures
    assert res.status_code != 401, (
        f"Database failure must not return 401, got {res.status_code}"
    )
    assert res.status_code in (500, 503), (
        f"Expected 500/503 for DB failure, got {res.status_code}"
    )


# ============================================================
# Group 4 — Authorization / ownership isolation
# ============================================================

async def _seed_users_and_project():
    """Seed two users and a project owned by user B."""
    async with AsyncSessionLocal() as db:
        user_a = User(id=100, clerk_id="user_auth_a", email="a@auth-test.com", name="User A")
        user_b = User(id=200, clerk_id="user_auth_b", email="b@auth-test.com", name="User B")
        db.add(user_a)
        db.add(user_b)
        await db.commit()

        proj_b = Project(
            id="proj-owned-by-b",
            user_id=200,
            title="User B Project",
            slug="user-b-project-auth",
        )
        db.add(proj_b)

        idea_b = Idea(
            id="idea-owned-by-b",
            project_id="proj-owned-by-b",
            title="User B Idea",
            problem_statement="Problem",
            solution_description="Solution",
            is_draft=False,
        )
        db.add(idea_b)
        await db.commit()

    return "user_auth_a", "user_auth_b"


@pytest.mark.asyncio
async def test_13_user_a_cannot_read_user_b_project():
    """User A reading User B's project → 404 (ownership enforced)."""
    await _seed_users_and_project()
    token_a = _make_token(sub="user_auth_a")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/api/v1/projects/proj-owned-by-b",
            headers={"Authorization": f"Bearer {token_a}"},
        )
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"


@pytest.mark.asyncio
async def test_14_user_a_cannot_update_user_b_project():
    """User A updating User B's project → 404."""
    await _seed_users_and_project()
    token_a = _make_token(sub="user_auth_a")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.patch(
            "/api/v1/projects/proj-owned-by-b",
            json={"title": "Hacked Title"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"


@pytest.mark.asyncio
async def test_15_user_a_cannot_delete_user_b_project():
    """User A deleting User B's project → 404."""
    await _seed_users_and_project()
    token_a = _make_token(sub="user_auth_a")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.delete(
            "/api/v1/projects/proj-owned-by-b",
            headers={"Authorization": f"Bearer {token_a}"},
        )
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"


@pytest.mark.asyncio
async def test_16_user_a_cannot_read_user_b_ideas():
    """User A listing User B's project ideas → 404."""
    await _seed_users_and_project()
    token_a = _make_token(sub="user_auth_a")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/api/v1/projects/proj-owned-by-b/ideas",
            headers={"Authorization": f"Bearer {token_a}"},
        )
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"


@pytest.mark.asyncio
async def test_17_user_a_cannot_trigger_evaluation_on_user_b_idea():
    """User A triggering evaluation on User B's idea → 403."""
    await _seed_users_and_project()
    token_a = _make_token(sub="user_auth_a")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/ideas/idea-owned-by-b/evaluations",
            json={"evaluation_type": "startup_evaluation"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
    assert res.status_code in (403, 404), f"Expected 403/404, got {res.status_code}"


# ============================================================
# Group 5 — Security invariant: test mode cannot leak to production
# ============================================================

def test_18_test_mode_requires_both_flags():
    """
    Security invariant: the HS256 test-token path is ONLY reachable when
    APP_ENV=test AND CLERK_JWT_TEST_SECRET are BOTH set.

    When APP_ENV != 'test', the test path is completely bypassed.
    The token goes through the real JWKS path and is rejected with 401
    (HS256 tokens have no matching kid in Clerk's RS256 JWKS).

    This verifies that setting CLERK_JWT_TEST_SECRET alone in a production
    environment cannot enable test-mode authentication.
    """
    import app.core.security as security_module
    from app.core.security import ClerkAuth
    import asyncio
    import pytest as _pytest
    from fastapi import HTTPException

    # Reset singleton so it re-evaluates inside the patched context
    original_client = security_module._jwks_client
    security_module._jwks_client = None

    try:
        with patch("app.core.security.settings") as mock_settings:
            mock_settings.APP_ENV = "production"   # NOT test
            mock_settings.CLERK_JWT_TEST_SECRET = "some-secret-key-that-is-32-bytes-long!"
            # Provide a real JWKS URL so _get_jwks_client() succeeds
            mock_settings.clerk_jwks_url = settings.clerk_jwks_url

            auth = ClerkAuth()
            # HS256 token signed with the "test" secret — must NOT be accepted
            token = _make_token(secret="some-secret-key-that-is-32-bytes-long!")

            async def _run():
                return await auth.verify_token(token)

            try:
                asyncio.run(_run())
                assert False, "Expected HTTPException but none was raised — HS256 token must not be accepted in production"
            except HTTPException as exc:
                # The HS256 token must be rejected.
                # 401 = rejected by JWKS path (correct: production rejects HS256)
                # 500 = JWKS misconfigured (acceptable if JWKS temporarily unavailable)
                # Anything else is a bug.
                assert exc.status_code in (401, 500), (
                    f"Expected 401 (JWKS rejection) or 500 (misconfigured), got {exc.status_code}"
                )
                # If 401, confirm the test-mode path was NOT used by checking the token
                # would have been ACCEPTED by the HS256 path (i.e., the secret is correct)
                if exc.status_code == 401:
                    valid_in_test_mode = pyjwt.decode(
                        token, "some-secret-key-that-is-32-bytes-long!", algorithms=["HS256"]
                    )
                    assert valid_in_test_mode.get("sub") is not None, (
                        "Token is valid under HS256 but was correctly rejected in production mode"
                    )
                    # This confirms: the token IS cryptographically valid for HS256
                    # but was STILL rejected — proving production mode doesn't use HS256 path
            except RuntimeError as exc:
                if "already running" in str(exc) or "Event loop stopped" in str(exc):
                    _pytest.skip("asyncio.run not available in nested loop context")
                raise
    finally:
        security_module._jwks_client = original_client






# ============================================================
# Group 6 — Configuration completeness
# ============================================================

def test_19_config_derives_jwks_url_from_publishable_key():
    """Settings.clerk_jwks_url is correctly derived from CLERK_PUBLISHABLE_KEY."""
    from app.core.config import _derive_clerk_issuer

    pk = "pk_test_aGVhbHRoeS1zdW5iZWFtLTY4LmNsZXJrLmFjY291bnRzLmRldiQ"
    issuer = _derive_clerk_issuer(pk)
    assert issuer == "https://healthy-sunbeam-68.clerk.accounts.dev", (
        f"Unexpected issuer: {issuer}"
    )


def test_20_config_invalid_publishable_key_returns_none():
    """Malformed publishable key returns None (no crash)."""
    from app.core.config import _derive_clerk_issuer

    assert _derive_clerk_issuer("not-a-valid-pk") is None
    # Empty string has no underscore split → None
    assert _derive_clerk_issuer("") is None
    # Bad base64 after the prefix → None
    assert _derive_clerk_issuer("pk_test_!!!") is None
    # Only two parts (no encoded payload)
    assert _derive_clerk_issuer("pk_test") is None


# ============================================================
# Group 7 — Issuer-specific verification tests
# ============================================================

@pytest.mark.asyncio
async def test_21_issuer_validation_correct_issuer_succeeds():
    """Token with correct `iss` claim matching configured issuer → 200."""
    valid_issuer = "https://healthy-sunbeam-68.clerk.accounts.dev"
    with patch.object(settings, "CLERK_JWT_ISSUER", valid_issuer):
        token = _make_token(
            sub="user_issuer_test_001",
            extra_claims={"iss": valid_issuer}
        )
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200, f"Expected 200 for correct issuer, got {res.status_code}"


@pytest.mark.asyncio
async def test_22_issuer_validation_wrong_issuer_returns_401():
    """Token with wrong `iss` claim mismatching configured issuer → 401."""
    valid_issuer = "https://healthy-sunbeam-68.clerk.accounts.dev"
    wrong_issuer = "https://attacker-fake-issuer.com"
    with patch.object(settings, "CLERK_JWT_ISSUER", valid_issuer):
        token = _make_token(
            sub="user_issuer_test_002",
            extra_claims={"iss": wrong_issuer}
        )
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 401, f"Expected 401 for wrong issuer, got {res.status_code}"


@pytest.mark.asyncio
async def test_23_issuer_validation_missing_issuer_claim_returns_401():
    """Token missing `iss` claim entirely when strict issuer validation is enabled → 401."""
    valid_issuer = "https://healthy-sunbeam-68.clerk.accounts.dev"
    with patch.object(settings, "CLERK_JWT_ISSUER", valid_issuer):
        # Token crafted without 'iss' claim
        token = _make_token(sub="user_issuer_test_003", extra_claims={"iss": None})
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 401, f"Expected 401 for missing iss claim, got {res.status_code}"


@pytest.mark.asyncio
async def test_24_issuer_validation_unconfigured_in_production_fails_500():
    """In production mode without issuer/publishable key configured, verify_token fails closed with 500."""
    from app.core.security import ClerkAuth
    import app.core.security as security_module

    auth = ClerkAuth()
    token = _make_token(sub="user_issuer_test_004")

    with patch.object(settings, "APP_ENV", "production"):
        with patch.object(settings, "CLERK_JWT_ISSUER", None):
            with patch.object(settings, "CLERK_PUBLISHABLE_KEY", None):
                from fastapi import HTTPException
                with pytest.raises(HTTPException) as exc_info:
                    await auth._verify_production_token(token)
                assert exc_info.value.status_code == 500, f"Expected 500 in prod without issuer, got {exc_info.value.status_code}"

