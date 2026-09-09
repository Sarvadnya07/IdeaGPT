# IdeaGPT — Production Environment Reference

**Product**: IdeaGPT  
**Version**: 1.0.0-rc1  
**Security Classification**: CONFIDENTIAL — OPERATIONAL REFERENCE  
**Audit Date**: August 2026  

---

## 1. Environment Variable Architecture & Classification

The IdeaGPT platform separates configuration into five strict tiers:
1. **PUBLIC**: Safe for client-side bundle embedding (`NEXT_PUBLIC_*`).
2. **SERVER_ONLY**: Backend runtime configuration required for application logic.
3. **SECRET**: Sensitive credentials and private cryptographic keys. Must NEVER be logged, committed, or exposed to the client.
4. **OPTIONAL**: Fallback providers, telemetry, and distributed caching enhancements.
5. **TEST_ONLY**: Explicitly restricted to unit/integration testing environments (`APP_ENV=test`).

---

## 2. Backend Environment Variables (`apps/api`)

| Variable Name | Tier | Required? | Purpose | Default / Example Value | Production Status |
| :--- | :---: | :---: | :--- | :--- | :---: |
| `APP_ENV` | `SERVER_ONLY` | **Yes** | Runtime environment switch (`development`, `test`, `production`). Enforces strict fail-fast validation in production. | `production` | 🟢 Standard Config |
| `PROJECT_NAME` | `SERVER_ONLY` | No | API service name displayed in health endpoints and OpenAPI metadata. | `IdeaGPT API` | 🟢 Standard Config |
| `VERSION` | `SERVER_ONLY` | No | Semantic version of the running API. | `1.0.0` | 🟢 Standard Config |
| `DATABASE_URL` | `SECRET` | **Yes** | PostgreSQL connection URI for SQLAlchemy asyncpg engine. | `postgresql+asyncpg://user:pass@host:5432/ideagpt_prod` | 🟡 Provision Live DB |
| `CORS_ORIGINS` | `SERVER_ONLY` | **Yes** | Comma-separated allowlist of web origins. Wildcards (`*`) are prohibited in production. | `https://app.ideagpt.dev,https://ideagpt.dev` | 🟡 Set Exact Domain |
| `CLERK_PUBLISHABLE_KEY` | `SERVER_ONLY` | **Yes** | Clerk publishable key (`pk_live_...` or `pk_test_...`) used to derive public JWKS URL. | `pk_live_...` | 🟡 Configure Clerk |
| `CLERK_JWT_ISSUER` | `SERVER_ONLY` | Optional | Explicit Clerk issuer URL. Overrides derived URL for strict domain verification. | `https://clerk.ideagpt.dev` | 🟡 Set Custom Domain |
| `CLERK_AUTHORIZED_PARTY`| `SERVER_ONLY` | Optional | Enforces authorized party (`azp`) claim match from Clerk frontend origin. | `https://app.ideagpt.dev` | 🟡 Set Custom Domain |
| `CLERK_SECRET_KEY` | `SECRET` | Optional | Clerk backend management secret key. Only required if executing backend Clerk Admin SDK actions. | `sk_live_...` | 🟢 Optional |
| `CLERK_JWT_TEST_SECRET` | `TEST_ONLY` | **NO** | Deterministic HS256 secret for automated tests. **Fails fast if present in `production`.** | `None` (Never set in prod) | 🟢 Isolated |
| `GROQ_API_KEY` | `SECRET` | **Yes** | Primary AI provider API key for LPU sub-second inference. | `gsk_...` | 🟢 Live Verified |
| `GROQ_BASE_URL` | `SERVER_ONLY` | No | Base URL for Groq OpenAI-compatible endpoints. | `https://api.groq.com/openai/v1` | 🟢 Default Active |
| `ENABLE_GROQ` | `SERVER_ONLY` | No | Explicit toggle for Groq provider. Defaults to auto-detection from key presence. | `true` | 🟢 Default Active |
| `OPENAI_API_KEY` | `SECRET` | Optional | Fallback AI provider key for GPT-4o / GPT-4o-mini. | `sk-proj-...` | 🟢 Optional Fallback |
| `ENABLE_OPENAI` | `SERVER_ONLY` | Optional | Toggle for OpenAI provider. | `true` (if key set) | 🟢 Optional Fallback |
| `GEMINI_API_KEY` | `SECRET` | Optional | Fallback AI provider key for Gemini 2.0 Flash. | `AIzaSy...` | 🟢 Optional Fallback |
| `ENABLE_GEMINI` | `SERVER_ONLY` | Optional | Toggle for Gemini provider. | `true` (if key set) | 🟢 Optional Fallback |
| `ENABLE_OLLAMA` | `SERVER_ONLY` | Optional | Toggle for local Ollama server. | `false` (in prod cloud) | 🟢 Disabled in Prod |
| `OLLAMA_URL` | `SERVER_ONLY` | Optional | Hostname for local Ollama instance. | `http://localhost:11434` | 🟢 Disabled in Prod |
| `REDIS_URL` | `SECRET` | Optional | Redis connection URI for distributed multi-pod rate limiting and caching. | `redis://user:pass@host:6379/0` | 🟢 Optional |
| `RATE_LIMIT_ENABLED` | `SERVER_ONLY` | No | Enables SlowAPI token bucket limiting on API endpoints. | `true` | 🟢 Active |
| `AI_EVALUATION_RATE_LIMIT`| `SERVER_ONLY` | No | Maximum evaluation requests per user per minute. | `5/minute` | 🟢 Active |
| `WRITE_API_RATE_LIMIT` | `SERVER_ONLY` | No | Maximum write requests per user per minute. | `30/minute` | 🟢 Active |

---

## 3. Frontend Environment Variables (`apps/web`)

| Variable Name | Tier | Required? | Purpose | Example Value | Production Status |
| :--- | :---: | :---: | :--- | :--- | :---: |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `PUBLIC` | **Yes** | Clerk publishable key initialized in browser client. | `pk_live_...` | 🟡 Configure Clerk |
| `CLERK_SECRET_KEY` | `SECRET` | **Yes** | Server-side Clerk key for Next.js App Router middleware validation. | `sk_live_...` | 🟡 Configure Clerk |
| `NEXT_PUBLIC_API_URL` | `PUBLIC` | **Yes** | Base URL for FastAPI backend endpoints. | `https://api.ideagpt.dev/api/v1` | 🟡 Set Backend URL |
| `BUILD_STANDALONE` | `SERVER_ONLY` | Optional | Triggers Next.js standalone container packaging. | `true` | 🟢 Supported |

---

## 4. Secret Isolation & Zero-Leakage Policy

1. **Client Bundle Scrutiny**: No variable without the `NEXT_PUBLIC_` prefix is accessible to the browser client.
2. **Server-Side API Keys**: `GROQ_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, and `DATABASE_URL` reside solely in backend memory and are never returned in HTTP responses.
3. **Log Sanitization**: `RequestLoggingMiddleware` scrubs URL parameters before writing JSON access logs to stdout.
