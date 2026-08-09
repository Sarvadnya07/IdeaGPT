"""
Test suite configuration for IdeaGPT API.

Key decisions:
  - DATABASE_URL forced to SQLite (in-process, no PostgreSQL needed for tests)
  - APP_ENV=test enables the HS256 test-token path in ClerkAuth
  - CLERK_JWT_TEST_SECRET must be set so tests can mint deterministic tokens
  - CLERK_PUBLISHABLE_KEY is intentionally absent in test mode
    (the real JWKS endpoint is never called during unit tests)

Security invariant:
  The test token mechanism is ONLY activated by the combination of
  APP_ENV=test AND CLERK_JWT_TEST_SECRET.  Setting only one of these
  in a production environment does nothing dangerous.
"""
import os
import pytest

# ---------------------------------------------------------------------------
# MUST be set before any app modules are imported — these are read at
# module import time by pydantic-settings.
# ---------------------------------------------------------------------------
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["APP_ENV"] = "test"
os.environ["CLERK_JWT_TEST_SECRET"] = "test-secret-for-unit-tests-only-never-production"
# No CLERK_PUBLISHABLE_KEY — the real JWKS endpoint must not be called in tests

# Force Celery to run in eager (synchronous) mode for testing
from app.workers.celery_app import celery_app
celery_app.conf.task_always_eager = True

# Import all models to register them with metadata
from app.db.base import Base
from app.models.user import User
from app.models.project import Project
from app.models.idea import Idea
from app.models.evaluation import Evaluation

from app.core.database import engine


@pytest.fixture(autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
