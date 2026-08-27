# IdeaGPT Security Architecture & Security Policy

Security is paramount for IdeaGPT. The platform processes proprietary startup ideas, financial projections, and integrates with third-party Large Language Models (LLMs).

---

## 1. Authentication & Authorization Security

1. **Fail-Closed Clerk JWT (RS256/JWKS):**
   - Authentication is verified on every protected route via RS256 cryptographic signatures using Clerk's official public JWKS.
   - Algorithms are strictly enforced (no algorithm confusion attacks).
   - In test mode, deterministic HS256 tokens require both `APP_ENV=test` and `CLERK_JWT_TEST_SECRET`.
   - Production configuration validator (`validate_production_config`) rejects insecure configurations at startup.

2. **Multi-Tenant Ownership Isolation (IDOR Defense):**
   - Every database query for projects, ideas, evaluations, and roadmaps strictly scopes by `user_id == current_user.id`.
   - Cross-user data access attempts return `404 Not Found` (to avoid resource enumeration) or `403 Forbidden`.

3. **Privilege Escalation Protection (Mass Assignment Defense):**
   - The user profile update schema (`UserUpdate`) explicitly excludes sensitive fields like `role` and `clerk_id`.
   - Attempting to pass `role: "admin"` during user self-update is ignored and prevented from modifying the database.

---

## 2. API & Infrastructure Security

1. **Decoupled Key Management:**
   - The Next.js frontend NEVER communicates directly with OpenAI, Anthropic, Groq, or any LLM provider.
   - All AI requests are proxied securely through the FastAPI backend (`apps/api`).

2. **CORS & Security Headers:**
   - The FastAPI backend strictly enforces allowed origins (`CORS_ORIGINS`). In production, wildcard `*` is explicitly blocked.
   - Next.js responses include `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Strict-Transport-Security`, `Permissions-Policy`, and strict `Content-Security-Policy` (CSP).

3. **Rate Limiting & Abuse Prevention:**
   - SlowAPI rate limiter with user-aware key function (`request.state.user_id` -> `clerk_id` -> IP fallback).
   - Tiered limits: AI evaluation (`5/min`), AI generation (`10/min`), write API (`30/min`), default (`60/min`).
   - Daily user quota enforcement (20 tasks/day/user).

4. **Container Security:**
   - Docker containers run under non-privileged system users (`appuser` in API, `nextjs` in Web).
   - No hardcoded secrets in `docker-compose.yml` or container layers.

---

## 3. Supply-Chain & CI/CD Security

1. **Least-Privilege GitHub Actions:**
   - Workflow runs with `permissions: contents: read` by default.
   - All third-party Actions are pinned to full 40-character commit SHAs.

2. **Automated Security Scanning:**
   - Dependabot configured for `pip`, `npm`, `github-actions`, and `docker` ecosystems with weekly scans.
   - CI pipeline executes `pip-audit` and `pnpm audit`.
   - `CODEOWNERS` enforces review for sensitive auth, security, CI, and dependency files.

3. **Dependency Pinning:**
   - Frontend and backend dependencies use strict version constraints rather than `latest`.

---

## 4. Operational & Log Security

1. **Log Sanitization:**
   - Database query logging (`echo=True`) is restricted to `APP_ENV=development` only.
   - Internal exception traces are logged server-side and never leaked in SSE streams or public health endpoints.
   - Operational endpoints (`/health/config`, `/health/ai`, `/health/providers`, `/metrics`) require authentication.
