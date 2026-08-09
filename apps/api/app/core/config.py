import base64
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


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
        env_file=".env",
        extra="ignore"
    )

    PROJECT_NAME: str = "IdeaGPT API"
    VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # development | test | production

    DATABASE_URL: Optional[str] = "sqlite+aiosqlite:///./ideagpt.db"
    REDIS_URL: Optional[str] = None

    # AI Providers (Loaded lazily, no placeholder text)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    DEFAULT_PROVIDER: str = "mock"
    ENABLE_OPENAI: bool = False
    ENABLE_GEMINI: bool = False
    ENABLE_OLLAMA: bool = False
    OLLAMA_URL: str = "http://localhost:11434"
    CUSTOM_PROVIDER_URL: Optional[str] = None
    CUSTOM_PROVIDER_KEY: Optional[str] = None

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

    def get_config_status(self) -> dict[str, str]:
        """
        Return the status of key security configuration variables without exposing sensitive secret values.
        """
        return {
            "APP_ENV": self.APP_ENV,
            "CLERK_PUBLISHABLE_KEY": "configured" if self.CLERK_PUBLISHABLE_KEY else "missing",
            "CLERK_JWT_ISSUER": "explicitly_configured" if self.CLERK_JWT_ISSUER else ("derived" if self.clerk_issuer else "missing"),
            "CLERK_SECRET_KEY": "configured" if self.CLERK_SECRET_KEY else "absent",
            "CLERK_JWT_TEST_SECRET": "configured" if self.CLERK_JWT_TEST_SECRET else "absent",
            "CORS_ORIGINS": f"configured ({len(self.cors_origins_list)} origins)" if self.cors_origins_list else "missing",
        }


settings = Settings()
