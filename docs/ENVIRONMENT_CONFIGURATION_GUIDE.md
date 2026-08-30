# IdeaGPT — Environment Configuration Architecture Guide

**Authoritative Standard**: Production & Development Environment Source-of-Truth  
**Security Classification**: OPERATIONAL REFERENCE  
**Audit Date**: August 2026  

---

## 1. Environment Source-of-Truth Architecture

IdeaGPT enforces a strict 4-tier separation of environment configuration to prevent secret leakage and eliminate runtime directory ambiguity:

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                        ENVIRONMENT SOURCE OF TRUTH                        │
├────────────────────────┬──────────────────────────────────────────────────┤
│ Local API Development  │ apps/api/.env (Local only, Git ignored)          │
├────────────────────────┼──────────────────────────────────────────────────┤
│ Local Web Development  │ apps/web/.env.local (Local only, Git ignored)    │
├────────────────────────┼──────────────────────────────────────────────────┤
│ Repository Template    │ .env.example & apps/api/.env.example (Committed) │
├────────────────────────┼──────────────────────────────────────────────────┤
│ Vercel Production API  │ Vercel Project Env Vars (idea-gpt-api project)   │
├────────────────────────┼──────────────────────────────────────────────────┤
│ Vercel Production Web  │ Vercel Project Env Vars (idea-gpt project)       │
└────────────────────────┴──────────────────────────────────────────────────┘
```

### Core Invariants
1. **No Root `.env` Requirement**: The application never requires or creates a root `.env` file.
2. **Deterministic Dynamic Discovery**: `apps/api/app/core/config.py` checks for `apps/api/.env` locally. If present, it loads it; if absent (as in Vercel serverless / Docker containers), it reads pure process environment variables from `os.environ`.
3. **Frontend / Backend Boundary**: Frontend projects receive only `NEXT_PUBLIC_*` public variables and server-side Clerk credentials (`CLERK_SECRET_KEY`). Database connection strings and AI provider keys (`DATABASE_URL`, `GROQ_API_KEY`, `OPENAI_API_KEY`) NEVER reach the frontend.
4. **Template Integrity**: `.env.example` contains only documentation placeholders. Real secrets must never be committed.

---

## 2. API Environment Variables Matrix (`apps/api`)

| Variable | Tier | Required in Prod? | Purpose | Safe Example Value |
| :--- | :---: | :---: | :--- | :--- |
| `APP_ENV` | `SERVER_ONLY` | **Yes** | Environment switch (`development`, `test`, `production`). | `production` |
| `PROJECT_NAME` | `SERVER_ONLY` | No | API service display title. | `IdeaGPT API` |
| `VERSION` | `SERVER_ONLY` | No | Semantic version tag. | `1.0.0` |
| `DATABASE_URL` | `SECRET` | **Yes** | PostgreSQL async connection string. | `postgresql+asyncpg://user:pass@host:5432/db` |
| `CORS_ORIGINS` | `SERVER_ONLY` | **Yes** | Exact comma-separated frontend origins (no `*` in prod). | `https://app.ideagpt.dev,https://ideagpt.dev` |
| `CLERK_PUBLISHABLE_KEY` | `SERVER_ONLY` | **Yes** | Clerk publishable key for public JWKS URL derivation. | `pk_live_...` |
| `CLERK_SECRET_KEY` | `SECRET` | Optional | Backend Clerk admin SDK secret key. | `sk_live_...` |
| `CLERK_JWT_ISSUER` | `SERVER_ONLY` | Optional | Explicit Clerk issuer domain override. | `https://clerk.ideagpt.dev` |
| `CLERK_AUTHORIZED_PARTY`| `SERVER_ONLY` | Optional | Authorized party `azp` validation. | `https://app.ideagpt.dev` |
| `CLERK_JWT_TEST_SECRET` | `TEST_ONLY` | **PROHIBITED** | HS256 secret for automated tests (rejected in prod). | `None` |
| `GROQ_API_KEY` | `SECRET` | **Yes** | Primary AI inference provider API key. | `gsk_...` |
| `GROQ_BASE_URL` | `SERVER_ONLY` | No | Groq API endpoint base URL. | `https://api.groq.com/openai/v1` |
| `GROQ_DEFAULT_MODEL` | `SERVER_ONLY` | No | Default candidate model (or `auto` for live discovery). | `auto` |
| `ENABLE_GROQ` | `SERVER_ONLY` | No | Explicit toggle for Groq adapter. | `true` |
| `OPENAI_API_KEY` | `SECRET` | Optional | Fallback AI provider key. | `sk-proj-...` |
| `ENABLE_OPENAI` | `SERVER_ONLY` | Optional | Toggle for OpenAI adapter. | `true` |
| `GEMINI_API_KEY` | `SECRET` | Optional | Fallback AI provider key. | `AIzaSy...` |
| `ENABLE_GEMINI` | `SERVER_ONLY` | Optional | Toggle for Gemini adapter. | `true` |
| `TAVILY_API_KEY` | `SECRET` | Optional | Web research provider API key. | `tvly-...` |
| `REDIS_URL` | `SECRET` | Optional | Redis connection URI for distributed rate limiting. | `redis://user:pass@host:6379/0` |
| `RATE_LIMIT_ENABLED` | `SERVER_ONLY` | No | Enables SlowAPI token bucket limiting. | `true` |

---

## 3. Web Environment Variables Matrix (`apps/web`)

| Variable | Tier | Required in Prod? | Purpose | Safe Example Value |
| :--- | :---: | :---: | :--- | :--- |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `PUBLIC` | **Yes** | Clerk publishable key initialized in browser client. | `pk_live_...` |
| `CLERK_SECRET_KEY` | `SECRET` | **Yes** | Server-side Clerk key for Next.js App Router middleware. | `sk_live_...` |
| `NEXT_PUBLIC_API_URL` | `PUBLIC` | **Yes** | Base URL for FastAPI backend endpoints. | `https://api.ideagpt.dev/api/v1` |
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | `PUBLIC` | No | Sign-in page path. | `/sign-in` |
| `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | `PUBLIC` | No | Sign-up page path. | `/sign-up` |
