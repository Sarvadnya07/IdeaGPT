from pathlib import Path
import base64
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List

# Locate apps/api/.env dynamically if present on local disk for development
_API_DIR = Path(__file__).resolve().parent.parent.parent
_LOCAL_ENV_FILE = _API_DIR / ".env"
_ENV_FILE_PATH = str(_LOCAL_ENV_FILE) if _LOCAL_ENV_FILE.exists() else None


def _derive_clerk_issuer(publishable_key: str) -> Optional[str]:
    """
    Derive the Clerk issuer URL from a Clerk publishable key.

    Clerk publishable keys are formatted as:
        pk_test_<base64url-encoded-frontend-api>
        pk_live_<base64url-encoded-frontend-api>

    The encoded payload decodes to something like:
        smart-duckling-70.clerk.accounts.dev$

    Stripping the trailing '$' gives the Clerk Frontend API host,
    and prepending 'https://' gives the issuer URL.
    """
    try:
        parts = publishable_key.split("_", 2)
        if len(parts) != 3 or parts[0] != "pk":
            return None
        encoded = parts[2]
        # Add padding if needed for standard base64
        padding = 4 - len(encoded) % 4
        if padding != 4:
            encoded += "=" * padding
        decoded = base64.b64decode(encoded).decode("utf-8").rstrip("$")
        # Sanity check: decoded host must be a non-empty hostname-like string
        if not decoded or "." not in decoded or any(c in decoded for c in " \t\n\r"):
            return None
        return f"https://{decoded}"
    except Exception:
        return None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE_PATH,
        extra="ignore"
    )

    PROJECT_NAME: str = "IdeaGPT API"
    VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # development | test | production

    DATABASE_URL: Optional[str] = "sqlite+aiosqlite:///./ideagpt.db"
    REDIS_URL: Optional[str] = None

    # Rate Limiting & Abuse Protection
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_STORAGE_URL: Optional[str] = None
    AI_EVALUATION_RATE_LIMIT: str = "5/minute"
    AI_GENERATION_RATE_LIMIT: str = "10/minute"
    WRITE_API_RATE_LIMIT: str = "30/minute"
    DEFAULT_API_RATE_LIMIT: str = "60/minute"

    # AI Providers (Loaded lazily, no placeholder text)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None

    DEFAULT_PROVIDER: str = "mock"
    ENABLE_OPENAI: bool = False
    ENABLE_GEMINI: bool = False
    ENABLE_OLLAMA: bool = False
    OLLAMA_URL: str = "http://localhost:11434"
    CUSTOM_PROVIDER_URL: Optional[str] = None
    CUSTOM_PROVIDER_KEY: Optional[str] = None

    GROQ_API_KEY: Optional[str] = None
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    ENABLE_GROQ: Optional[bool] = None
    GROQ_DEFAULT_MODEL: str = "auto"

    # ---------------------------------------------------------------------------
    # Clerk Authentication
    #
    # CLERK_PUBLISHABLE_KEY is used to derive the issuer URL and JWKS endpoint.
    # The JWKS endpoint (/.well-known/jwks.json) is public — no secret key is
    # required to fetch it.
    #
    # CLERK_SECRET_KEY is NOT required for JWT verification and should NOT be
    # placed in the API .env unless you explicitly need Clerk backend API calls
    # (e.g., user management, webhooks).  Do NOT expose it to the frontend.
    #
    # CLERK_JWT_ISSUER optionally overrides the issuer derived from the
    # publishable key.  Set this in production for strict validation.
    #
    # CLERK_AUTHORIZED_PARTY optionally enforces the `azp` claim (authorized
    # party), which Clerk sets to the origin of the session.
    #
    # CLERK_JWT_TEST_SECRET enables deterministic HS256 test tokens ONLY when
    # APP_ENV=test.  Never set this in production.
    # ---------------------------------------------------------------------------
    CLERK_PUBLISHABLE_KEY: Optional[str] = None
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_JWT_ISSUER: Optional[str] = None        # optional: overrides derived issuer
    CLERK_AUTHORIZED_PARTY: Optional[str] = None  # optional: validates azp claim
    CLERK_JWT_TEST_SECRET: Optional[str] = None   # test mode only — never production

    # ---------------------------------------------------------------------------
    # CORS
    # Comma-separated list of allowed origins.
    # Example: CORS_ORIGINS=http://localhost:3000,https://ideagpt.dev
    # ---------------------------------------------------------------------------
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def clerk_issuer(self) -> Optional[str]:
        """
        Returns the Clerk issuer URL.
        Priority: explicit CLERK_JWT_ISSUER → derived from CLERK_PUBLISHABLE_KEY → None
        """
        if self.CLERK_JWT_ISSUER:
            return self.CLERK_JWT_ISSUER
        if self.CLERK_PUBLISHABLE_KEY:
            return _derive_clerk_issuer(self.CLERK_PUBLISHABLE_KEY)
        return None

    @property
    def clerk_jwks_url(self) -> Optional[str]:
        """Returns the Clerk JWKS endpoint URL, or None if unconfigured."""
        issuer = self.clerk_issuer
        if issuer:
            return f"{issuer.rstrip('/')}/.well-known/jwks.json"
        return None

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse the comma-separated CORS_ORIGINS into a list."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def async_database_url(self) -> str:
        """
        Normalize DATABASE_URL for SQLAlchemy async engine (asyncpg or aiosqlite).
        Standard postgresql:// or postgresql+psycopg2:// URLs are safely normalized to postgresql+asyncpg://.
        """
        raw = self.DATABASE_URL or "sqlite+aiosqlite:///./ideagpt.db"
        try:
            from sqlalchemy.engine import make_url
            u = make_url(raw)
            if u.drivername in ("postgresql", "postgres", "postgresql+psycopg2"):
                u = u.set(drivername="postgresql+asyncpg")
            elif u.drivername == "sqlite":
                u = u.set(drivername="sqlite+aiosqlite")
            return u.render_as_string(hide_password=False)
        except Exception:
            return raw

    @property
    def sync_database_url(self) -> str:
        """
        Normalize DATABASE_URL for synchronous tools such as Alembic (psycopg2 or sqlite).
        """
        raw = self.DATABASE_URL or "sqlite:///./ideagpt.db"
        try:
            from sqlalchemy.engine import make_url
            u = make_url(raw)
            if u.drivername in ("postgresql+asyncpg", "postgres", "postgresql"):
                u = u.set(drivername="postgresql+psycopg2")
            elif u.drivername == "sqlite+aiosqlite":
                u = u.set(drivername="sqlite")
            return u.render_as_string(hide_password=False)
        except Exception:
            return raw

    def validate_production_config(self):
        """
        Validates critical configuration parameters when running in production mode.
        Fails fast with RuntimeError if insecure or missing settings are detected.
        """
        if self.APP_ENV == "production":
            if not self.clerk_issuer:
                raise RuntimeError("PRODUCTION CONFIG ERROR: CLERK_PUBLISHABLE_KEY or CLERK_JWT_ISSUER must be configured in production.")
            if self.CLERK_JWT_TEST_SECRET:
                raise RuntimeError("PRODUCTION CONFIG SECURITY ERROR: CLERK_JWT_TEST_SECRET must NOT be set in production.")
            if "*" in self.cors_origins_list:
                raise RuntimeError("PRODUCTION CONFIG SECURITY ERROR: CORS_ORIGINS cannot contain wildcard '*' in production.")
            if "sqlite" in (self.async_database_url or ""):
                raise RuntimeError("PRODUCTION CONFIG ERROR: SQLite DATABASE_URL cannot be used in production. PostgreSQL is required.")

    def get_config_status(self) -> dict[str, str]:
        """
        Return the status of key security configuration variables without exposing sensitive secret values.
        """
        return {
            "APP_ENV": self.APP_ENV,
            "DATABASE_DRIVER": "asyncpg" if "asyncpg" in self.async_database_url else ("aiosqlite" if "sqlite" in self.async_database_url else "other"),
            "CLERK_PUBLISHABLE_KEY": "configured" if self.CLERK_PUBLISHABLE_KEY else "missing",
            "CLERK_JWT_ISSUER": "explicitly_configured" if self.CLERK_JWT_ISSUER else ("derived" if self.clerk_issuer else "missing"),
            "CLERK_SECRET_KEY": "configured" if self.CLERK_SECRET_KEY else "absent",
            "CLERK_JWT_TEST_SECRET": "configured" if self.CLERK_JWT_TEST_SECRET else "absent",
            "CORS_ORIGINS": f"configured ({len(self.cors_origins_list)} origins)" if self.cors_origins_list else "missing",
        }


settings = Settings()
try:
    settings.validate_production_config()
except RuntimeError as err:
    import logging
    logging.getLogger("uvicorn.error").error(str(err))

