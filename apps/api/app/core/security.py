"""
Clerk JWT verification using PyJWT's built-in PyJWKClient.

Strategy:
  - JWKS endpoint is derived from CLERK_PUBLISHABLE_KEY (public endpoint, no secret needed)
  - PyJWKClient handles fetching, caching (5-min TTL), and key rotation automatically
  - Algorithm is enforced to RS256 only
  - exp, nbf, iss (when configured) are validated
  - azp is validated when CLERK_AUTHORIZED_PARTY is configured
  - sub is mandatory

Test mode (APP_ENV=test + CLERK_JWT_TEST_SECRET set):
  - Accepts HS256 tokens signed with the test secret
  - This mode is EXPLICITLY isolated and cannot activate in production
  - NEVER set CLERK_JWT_TEST_SECRET in a production environment

Fail-closed rules:
  - Missing CLERK_PUBLISHABLE_KEY outside test mode → authentication failure
  - Invalid signature → 401
  - Expired token → 401
  - Missing sub → 401
  - Any configuration error → authentication failure (never silent bypass)
"""

import logging
from typing import Any

import jwt
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PyJWKClient singleton — initialized lazily on first request.
# PyJWKClient has a two-tier cache (JWK Set + signing key).
# Default lifespan=300s (5 minutes).  On kid miss it re-fetches automatically.
# ---------------------------------------------------------------------------
_jwks_client: jwt.PyJWKClient | None = None


def _get_jwks_client() -> jwt.PyJWKClient:
    """
    Return the cached PyJWKClient, creating it on first call.

    Raises HTTPException 500 if the JWKS URL cannot be determined
    (missing CLERK_PUBLISHABLE_KEY and CLERK_JWT_ISSUER).
    """
    global _jwks_client

    if _jwks_client is not None:
        return _jwks_client

    jwks_url = settings.clerk_jwks_url
    if not jwks_url:
        logger.critical(
            "Clerk JWKS URL could not be determined. "
            "Set CLERK_PUBLISHABLE_KEY or CLERK_JWT_ISSUER in the API environment. "
            "Authentication is unavailable."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service misconfigured",
        )

    logger.info("Initialising Clerk JWKS client — URL: %s", jwks_url)
    _jwks_client = jwt.PyJWKClient(
        jwks_url,
        cache_jwk_set=True,
        lifespan=300,  # 5-minute cache
    )
    return _jwks_client


class ClerkAuth:
    """
    Clerk JWT verifier.  The class shell is preserved from the existing
    architecture so that all call sites (auth.py) remain unchanged.
    """

    def __init__(self) -> None:
        pass  # JWKS client is module-level singleton

    async def verify_token(self, token: str) -> dict[str, Any]:
        """
        Cryptographically verify a Clerk session JWT.

        Returns the verified payload dict on success.
        Raises HTTPException 401 on any verification failure.
        Raises HTTPException 500 if authentication is misconfigured.

        NEVER falls back to unverified decoding.
        """
        # ------------------------------------------------------------------
        # TEST MODE — HS256 with a deterministic secret
        # Activated ONLY when APP_ENV=test AND CLERK_JWT_TEST_SECRET is set.
        # Production environments must never set CLERK_JWT_TEST_SECRET.
        # ------------------------------------------------------------------
        if settings.APP_ENV == "test" and settings.CLERK_JWT_TEST_SECRET:
            return self._verify_test_token(token)

        # ------------------------------------------------------------------
        # PRODUCTION / DEVELOPMENT — Full RS256 JWKS verification
        # ------------------------------------------------------------------
        return await self._verify_production_token(token)

    def _verify_test_token(self, token: str) -> dict[str, Any]:
        """
        Verify a deterministic HS256 test token.

        This path is ONLY reachable when APP_ENV=test AND
        CLERK_JWT_TEST_SECRET is explicitly set.  It allows the test suite
        to create signed tokens without calling the real Clerk service.
        """
        assert settings.APP_ENV == "test", (
            "BUG: _verify_test_token called outside test mode"
        )
        assert settings.CLERK_JWT_TEST_SECRET, (
            "BUG: _verify_test_token called without CLERK_JWT_TEST_SECRET"
        )

        try:
            # Reject anything that isn't HS256 — no algorithm confusion
            header = jwt.get_unverified_header(token)
            if header.get("alg") != "HS256":
                raise jwt.InvalidAlgorithmError(
                    "Test mode only accepts HS256 tokens"
                )

            options: dict[str, Any] = {"require": ["sub", "exp"]}
            issuer = settings.clerk_issuer
            if issuer:
                options["require"].append("iss")

            payload = jwt.decode(
                token,
                settings.CLERK_JWT_TEST_SECRET,
                algorithms=["HS256"],
                options=options,
                issuer=issuer,
            )
            return payload

        except jwt.ExpiredSignatureError:
            logger.info("Test token rejected: expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidIssuerError:
            logger.warning("Test token rejected: issuer mismatch")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.MissingRequiredClaimError as exc:
            logger.info("Test token rejected: missing required claim — %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as exc:
            logger.info("Test token rejected: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def _verify_production_token(self, token: str) -> dict[str, Any]:
        """
        Verify a real Clerk RS256 JWT against the live JWKS endpoint.

        Steps:
          1. Reject non-RS256 algorithms from the unverified header.
          2. Resolve the signing key by kid via PyJWKClient (cached JWKS).
          3. Decode and verify: signature, exp, nbf, iss (strict in prod or when configured).
          4. Validate azp if CLERK_AUTHORIZED_PARTY is configured.
          5. Require sub.
        """
        issuer = settings.clerk_issuer

        # Production mode requires explicit/derived issuer configuration — fail closed
        if settings.APP_ENV == "production" and not issuer:
            logger.critical(
                "Production environment requires strict Clerk issuer configuration. "
                "Set CLERK_PUBLISHABLE_KEY or CLERK_JWT_ISSUER."
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service misconfigured",
            )

        # Step 1 — reject non-RS256 before touching the network
        try:
            header = jwt.get_unverified_header(token)
        except jwt.DecodeError as exc:
            logger.info("Token header unparseable: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        alg = header.get("alg", "")
        if alg != "RS256":
            logger.warning(
                "Token rejected: unexpected algorithm '%s' (expected RS256)", alg
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Step 2 — resolve signing key (uses cached JWKS; re-fetches on kid miss)
        client = _get_jwks_client()
        try:
            signing_key = client.get_signing_key_from_jwt(token)
        except jwt.exceptions.PyJWKClientError as exc:
            logger.warning("JWKS key resolution failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as exc:
            # Network error fetching JWKS — treat as server-side failure
            logger.error("JWKS fetch error: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service temporarily unavailable",
            )

        # Step 3 — decode with full verification
        decode_options: dict[str, Any] = {
            "require": ["sub", "exp", "iat"],
            "verify_signature": True,
            "verify_exp": True,
            "verify_nbf": True,
            "verify_iat": True,
        }
        if issuer or settings.APP_ENV == "production":
            decode_options["require"].append("iss")
            decode_options["verify_iss"] = True

        try:
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options=decode_options,
                issuer=issuer,
            )
        except jwt.ExpiredSignatureError:
            logger.info("Token rejected: expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidIssuerError:
            logger.warning(
                "Token rejected: issuer mismatch (expected '%s')", issuer
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.ImmatureSignatureError:
            logger.info("Token rejected: not yet valid (nbf)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not yet valid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidSignatureError:
            logger.warning("Token rejected: invalid signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.MissingRequiredClaimError as exc:
            logger.info("Token rejected: missing required claim — %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as exc:
            logger.info("Token rejected: %s — %s", type(exc).__name__, exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if issuer is None:
            logger.warning(
                "Issuer validation skipped — set CLERK_PUBLISHABLE_KEY or "
                "CLERK_JWT_ISSUER to enable strict issuer checks"
            )

        # Step 4 — azp (authorized party) validation
        authorized_party = settings.CLERK_AUTHORIZED_PARTY
        if authorized_party:
            azp = payload.get("azp")
            if azp != authorized_party:
                logger.warning(
                    "Token rejected: azp '%s' does not match expected '%s'",
                    azp,
                    authorized_party,
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # Step 5 — sub is mandatory (also enforced by "require" above,
        # but an explicit check gives a more descriptive log line)
        if not payload.get("sub"):
            logger.warning("Token rejected: missing sub claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload
