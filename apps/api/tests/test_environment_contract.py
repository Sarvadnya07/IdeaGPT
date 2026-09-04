"""
IdeaGPT Environment & Configuration Contract Test Suite.
Verifies fail-fast production rules, development defaults, asyncpg normalization,
secret masking in health/status endpoints, and process-only environment loading.
"""

import pytest
from app.core.config import Settings, _derive_clerk_issuer


def test_derive_clerk_issuer():
    """Verify base64 extraction of Clerk Frontend API host from publishable key."""
    # Base64 of 'smart-duckling-70.clerk.accounts.dev$'
    pk = "pk_test_c21hcnQtZHVja2xpbmctNzAuY2xlcmsuYWNjb3VudHMuZGV2JA"
    issuer = _derive_clerk_issuer(pk)
    assert issuer == "https://smart-duckling-70.clerk.accounts.dev"

    # Invalid keys return None gracefully
    assert _derive_clerk_issuer("invalid_key") is None
    assert _derive_clerk_issuer("pk_invalid") is None
    assert _derive_clerk_issuer("") is None


def test_database_url_normalizes_to_asyncpg():
    """Verify PostgreSQL connection strings are safely converted to asyncpg dialect."""
    s = Settings(
        DATABASE_URL="postgresql://dbuser:secretpass@dbhost:5432/ideagpt",
        _env_file=None
    )
    assert "postgresql+asyncpg://" in s.async_database_url
    assert "secretpass" in s.async_database_url

    s2 = Settings(
        DATABASE_URL="postgresql+psycopg2://dbuser:secretpass@dbhost:5432/ideagpt",
        _env_file=None
    )
    assert "postgresql+asyncpg://" in s2.async_database_url

    s3 = Settings(
        DATABASE_URL="sqlite:///./ideagpt.db",
        _env_file=None
    )
    assert "sqlite+aiosqlite://" in s3.async_database_url


def test_sync_database_url_normalizes_for_alembic():
    """Verify asynchronous connection strings normalize to sync drivers for Alembic."""
    s = Settings(
        DATABASE_URL="postgresql+asyncpg://dbuser:secretpass@dbhost:5432/ideagpt",
        _env_file=None
    )
    assert "postgresql+psycopg2://" in s.sync_database_url

    s2 = Settings(
        DATABASE_URL="sqlite+aiosqlite:///./ideagpt.db",
        _env_file=None
    )
    assert s2.sync_database_url == "sqlite:///./ideagpt.db"


def test_settings_instantiates_without_env_file():
    """Verify Settings works purely from process environment with env_file=None."""
    s = Settings(
        APP_ENV="test",
        PROJECT_NAME="Isolated Test",
        _env_file=None
    )
    assert s.APP_ENV == "test"
    assert s.PROJECT_NAME == "Isolated Test"


def test_production_rejects_missing_clerk_config():
    """Verify production fails fast if no Clerk configuration is provided."""
    s = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db",
        CLERK_PUBLISHABLE_KEY=None,
        CLERK_JWT_ISSUER=None,
        CLERK_JWT_TEST_SECRET=None,
        CORS_ORIGINS="https://app.ideagpt.dev",
        _env_file=None
    )
    with pytest.raises(RuntimeError, match="CLERK_PUBLISHABLE_KEY or CLERK_JWT_ISSUER must be configured in production"):
        s.validate_production_config()


def test_production_rejects_wildcard_cors():
    """Verify production fails fast if CORS contains wildcard '*'."""
    s = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db",
        CLERK_PUBLISHABLE_KEY="pk_test_c21hcnQtZHVja2xpbmctNzAuY2xlcmsuYWNjb3VudHMuZGV2JA",
        CLERK_JWT_TEST_SECRET=None,
        CORS_ORIGINS="https://app.ideagpt.dev, *",
        _env_file=None
    )
    with pytest.raises(RuntimeError, match="CORS_ORIGINS cannot contain wildcard"):
        s.validate_production_config()


def test_production_rejects_sqlite_database():
    """Verify production fails fast if SQLite database is configured."""
    s = Settings(
        APP_ENV="production",
        DATABASE_URL="sqlite+aiosqlite:///./ideagpt.db",
        CLERK_PUBLISHABLE_KEY="pk_test_c21hcnQtZHVja2xpbmctNzAuY2xlcmsuYWNjb3VudHMuZGV2JA",
        CLERK_JWT_TEST_SECRET=None,
        CORS_ORIGINS="https://app.ideagpt.dev",
        _env_file=None
    )
    with pytest.raises(RuntimeError, match="SQLite DATABASE_URL cannot be used in production"):
        s.validate_production_config()



def test_production_rejects_test_jwt_secret():
    """Verify production fails fast if CLERK_JWT_TEST_SECRET is set."""
    s = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db",
        CLERK_PUBLISHABLE_KEY="pk_test_c21hcnQtZHVja2xpbmctNzAuY2xlcmsuYWNjb3VudHMuZGV2JA",
        CLERK_JWT_TEST_SECRET="forbidden-in-production",
        CORS_ORIGINS="https://app.ideagpt.dev",
        _env_file=None
    )
    with pytest.raises(RuntimeError, match="CLERK_JWT_TEST_SECRET must NOT be set in production"):
        s.validate_production_config()


def test_production_rejects_missing_credential_encryption_key():
    """Verify production fails fast if CREDENTIAL_ENCRYPTION_KEY is missing."""
    s = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db",
        CLERK_PUBLISHABLE_KEY="pk_test_c21hcnQtZHVja2xpbmctNzAuY2xlcmsuYWNjb3VudHMuZGV2JA",
        CLERK_JWT_TEST_SECRET=None,
        CORS_ORIGINS="https://app.ideagpt.dev",
        CREDENTIAL_ENCRYPTION_KEY=None,
        _env_file=None
    )
    with pytest.raises(RuntimeError, match="CREDENTIAL_ENCRYPTION_KEY must be configured in production"):
        s.validate_production_config()


def test_production_accepts_valid_configuration():
    """Verify production passes validation when all production settings are properly set."""
    s = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db",
        CLERK_PUBLISHABLE_KEY="pk_test_c21hcnQtZHVja2xpbmctNzAuY2xlcmsuYWNjb3VudHMuZGV2JA",
        CLERK_JWT_TEST_SECRET=None,
        CORS_ORIGINS="https://app.ideagpt.dev,https://ideagpt.dev",
        CREDENTIAL_ENCRYPTION_KEY="production-super-secret-key-configured-properly",
        _env_file=None
    )
    # Should not raise any exception
    s.validate_production_config()


def test_get_config_status_masks_secrets():
    """Verify get_config_status exposes only descriptive status strings, never raw secrets."""
    s = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql+asyncpg://user:super_secret_password@host:5432/db",
        CLERK_PUBLISHABLE_KEY="pk_test_c21hcnQtZHVja2xpbmctNzAuY2xlcmsuYWNjb3VudHMuZGV2JA",
        CLERK_SECRET_KEY="sk_live_super_secret_clerk_key",
        CORS_ORIGINS="https://app.ideagpt.dev",
        _env_file=None
    )
    status = s.get_config_status()

    # Confirm key presence
    assert status["APP_ENV"] == "production"
    assert status["DATABASE_DRIVER"] == "asyncpg"
    assert status["CLERK_PUBLISHABLE_KEY"] == "configured"
    assert status["CLERK_SECRET_KEY"] == "configured"

    # Confirm zero secret leakage
    status_str = str(status)
    assert "super_secret_password" not in status_str
    assert "sk_live_super_secret_clerk_key" not in status_str


def test_optional_providers_do_not_crash_startup():
    """Verify unconfigured optional AI providers default to disabled/None without error."""
    s = Settings(
        OPENAI_API_KEY=None,
        GEMINI_API_KEY=None,
        ANTHROPIC_API_KEY=None,
        TAVILY_API_KEY=None,
        _env_file=None
    )
    assert s.OPENAI_API_KEY is None
    assert s.GEMINI_API_KEY is None
    assert s.ANTHROPIC_API_KEY is None
    assert s.TAVILY_API_KEY is None
    assert s.ENABLE_OPENAI is False
    assert s.ENABLE_GEMINI is False
