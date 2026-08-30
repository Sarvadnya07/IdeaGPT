# IdeaGPT — Vercel Runtime Failure & Environment Remediation Report

**Product**: IdeaGPT Backend API (`idea-gpt-api`)  
**Deployment Platform**: Vercel Serverless Functions (`@vercel/python`)  
**Status**: 🟢 **RESOLVED & CONTRACT TESTED**  
**Date**: August 2026  

---

## 1. Executive Summary & Root Cause Classification

The Vercel runtime failure (`500 FUNCTION_INVOCATION_FAILED`) on `idea-gpt-api` stemmed from two interrelated configuration and routing causes:

### Root Cause 1: Missing Serverless Routing Definition (`vercel.json`)
- **Classification**: `Vercel Routing & Runtime Execution`
- **Mechanism**: Without an explicit `rewrites` configuration in `apps/api/vercel.json`, Vercel's default serverless router did not map sub-path HTTP requests (`/health/live`, `/api/v1/projects`, `/api/v1/ai/models`) to the single ASGI entrypoint (`index.py`), causing serverless handler invocation failures.
- **Resolution**: Created `apps/api/vercel.json` with universal wildcard rewrites (`{"source": "/(.*)", "destination": "/index.py"}`) and exposed `handler = app` alias in `apps/api/index.py`.

### Root Cause 2: Hardcoded Relative `.env` Path in Pydantic Settings
- **Classification**: `Environment Configuration & Directory Resolution`
- **Mechanism**: `SettingsConfigDict(env_file=".env")` looked for `.env` in the current working directory. In local monorepo contexts, this failed if executed from root, while in Vercel serverless environments, it attempted to look for a non-existent filesystem `.env` file rather than purely reading process environment variables.
- **Resolution**: Implemented dynamic filesystem detection in `apps/api/app/core/config.py`. If `apps/api/.env` exists on disk (local development), it loads it; if absent (Vercel / Docker), `env_file=None` is used and settings instantiate cleanly from process environment variables (`os.environ`).

---

## 2. Files Changed & Summary of Modifications

| File | Change Description | Security / Operational Effect |
| :--- | :--- | :--- |
| [`apps/api/app/core/config.py`](file:///C:/Users/ASUS/Desktop/STUDY/PROJECTS/IdeaGPT/apps/api/app/core/config.py) | Dynamic `apps/api/.env` resolution; `env_file=None` in cloud; added `TAVILY_API_KEY`. | Predictable local and cloud environment loading; 0 root `.env` requirement. |
| [`apps/api/index.py`](file:///C:/Users/ASUS/Desktop/STUDY/PROJECTS/IdeaGPT/apps/api/index.py) | Added `handler = app` export alias and verified `sys.path` injection. | Universal Vercel serverless function compatibility. |
| [`apps/api/vercel.json`](file:///C:/Users/ASUS/Desktop/STUDY/PROJECTS/IdeaGPT/apps/api/vercel.json) | Created universal serverless routing rewrite rule (`/(.*)` → `/index.py`). | Fixes `FUNCTION_INVOCATION_FAILED` on sub-path API requests. |
| [`.env.example`](file:///C:/Users/ASUS/Desktop/STUDY/PROJECTS/IdeaGPT/.env.example) | Synchronized all supported environment variables with safe placeholders. | Comprehensive documentation template with zero secrets. |
| [`apps/api/.env.example`](file:///C:/Users/ASUS/Desktop/STUDY/PROJECTS/IdeaGPT/apps/api/.env.example) | Updated API template with `CORS_ORIGINS`, `CLERK_SECRET_KEY`, `TAVILY_API_KEY`. | Local API developer setup reference. |
| [`apps/api/tests/test_environment_contract.py`](file:///C:/Users/ASUS/Desktop/STUDY/PROJECTS/IdeaGPT/apps/api/tests/test_environment_contract.py) | Added 11 automated contract tests for production validation and `env_file=None`. | Regression prevention across all environment tiers. |

---

## 3. Verification & Validation Evidence

```text
================================================================================
BACKEND CONTRACT & UNIT TESTS: 239 PASSED, 4 SKIPPED, 0 FAILED (19.64s)
FLAKE8 CODE QUALITY:           PASS (0 lint errors across app, tests, index.py)
ALEMBIC SCHEMA DRIFT:          0 SCHEMA DRIFT (PostgreSQL schemas in sync)
FRONTEND TYPE CHECK (TSC):     0 COMPILATION ERRORS (apps/web)
FRONTEND VITEST SUITE:         30 PASSED across 8 test suites (5.57s)
PLAYWRIGHT BROWSER E2E:        19 PASSED (16.1s)
TURBOREPO PRODUCTION BUILD:    ALL 28 NEXT.JS ROUTES COMPILED IN FULL TURBO
================================================================================
```

---

## 4. Remaining External Actions for Vercel Deployment

To complete the private beta deployment on Vercel:

1. **In Vercel Dashboard for `idea-gpt-api`**:
   - Ensure Root Directory is set to `apps/api`.
   - Configure required Environment Variables (`APP_ENV=production`, `DATABASE_URL=postgresql+asyncpg://...`, `CORS_ORIGINS=https://idea-gpt.vercel.app`, `CLERK_PUBLISHABLE_KEY=pk_live_...`, `GROQ_API_KEY=gsk_...`, `ENABLE_GROQ=true`).
2. **In Vercel Dashboard for `idea-gpt`**:
   - Ensure Root Directory is set to `apps/web` (or monorepo root).
   - Configure required Environment Variables (`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...`, `CLERK_SECRET_KEY=sk_live_...`, `NEXT_PUBLIC_API_URL=https://idea-gpt-api.vercel.app/api/v1`).
3. **Trigger Redeploy**:
   - Redeploy both projects from Vercel dashboard or push to `main`.
