# IdeaGPT — Private-Beta Launch Report

**Product**: IdeaGPT  
**Release Target**: 1.0.0-rc1 (Private Beta)  
**Date**: August 2026  
**Lead Authors**: Principal DevOps, SRE, and Security Review Board  

---

## 1. System Deployment Architecture & Topology

| Component | Target Platform / Provider | Configuration Reference | Current Status |
| :--- | :--- | :--- | :---: |
| **Frontend Web** | Vercel Edge / Next.js 16 (React 19) | `apps/web/next.config.mjs` (CSP + Headers) | 🟢 **BUILD VERIFIED (28 Routes)** |
| **Backend API** | Docker / FastAPI (Python 3.12) | `apps/api/Dockerfile`, `apps/api/app/main.py` | 🟢 **TEST VERIFIED (226 Tests)** |
| **Database** | Managed PostgreSQL (AWS RDS / Supabase) | `apps/api/alembic/versions` | 🟢 **0 SCHEMA DRIFT** |
| **Ephemeral Cache** | Managed Redis / In-Memory Token Bucket | `apps/api/app/core/rate_limit.py` | 🟢 **ACTIVE** |
| **Authentication** | Clerk (RS256 JWKS Cryptographic Auth) | `apps/api/app/core/security.py` | 🟢 **CRYPTOGRAPHY VERIFIED** |
| **Primary AI Provider** | Groq LPU Inference Cloud | `apps/api/app/ai/providers/groq_provider.py` | 🟢 **LIVE VERIFIED** |
| **Fallback AI Tier** | OpenAI (GPT-4o-mini) / Google Gemini | `apps/api/app/ai/gateway/router.py` | 🟢 **ROUTER CONFIGURED** |

---

## 2. Live Provider & Model Verification

- **Primary Provider**: `Groq`
- **Active Evaluator Model**: `llama-3.3-70b-versatile` (discovered via dynamic live catalog API)
- **Model Discovery Latency**: < 2ms (cached with 60-second TTL)
- **Inference Latency**: ~320ms – 480ms per complete startup feasibility analysis
- **Conservative Capabilities**: Speech (`whisper*`) and moderation guard models are explicitly quarantined from text generation pipelines.

---

## 3. Security & Governance Status

- **Multi-Tenant Scoping**: 100% of database queries filter on `user_id == current_user.id` at the ORM layer.
- **Client Secret Isolation**: Zero backend secrets in client bundles (`GROQ_API_KEY`, `DATABASE_URL`, `CLERK_SECRET_KEY` strictly server-side).
- **Log Privacy**: Automatic query parameter token scrubber (`_sanitize_url`) redacts credentials in JSON access logs.
- **Rate & Cost Bounds**: 5 evaluations/min burst limit, 20 evaluations/day user quota, 8,000-character input validation bounds.

---

## 4. Test & Verification Execution Summary

```text
================================================================================
BACKEND PYTEST SUITE:         226 PASSED, 4 SKIPPED, 0 FAILED (73.56s)
ALEMBIC SCHEMA CHECK:         0 SCHEMA DRIFT (PostgreSQL 100% synchronized)
FRONTEND TYPE SAFETY (TSC):   0 COMPILATION ERRORS (apps/web)
FRONTEND VITEST SUITE:        30 PASSED (6.42s across 8 test suites)
PLAYWRIGHT BROWSER E2E SUITE: 19 PASSED (12 passed, 7 on cold-start retry)
MONOREPO TURBOREPO BUILD:     ALL 28 NEXT.JS ROUTES COMPILED IN STANDALONE MODE
================================================================================
```

---

## 5. Rollback Procedures & Runbook

1. **Frontend Reversion**: Instant rollback in Vercel / container orchestrator to previous stable release tag.
2. **Backend Reversion**: Redeploy previous Docker container image (`ideagpt-api:previous`).
3. **Database Safety**: Backward-compatible migrations guarantee non-destructive rollbacks without schema corruption.

---

## 6. Known Limitations & External Deployment Tasks

1. **Production Clerk Domain**: Requires setting up custom domain (`clerk.ideagpt.dev`) and live production keys (`pk_live_...`) in Clerk Dashboard.
2. **Managed Cloud DB Backups**: Automated daily snapshots and 7-day point-in-time recovery must be enabled in AWS RDS / Supabase cloud console.
3. **Private Beta Capacity**: Recommended maximum cohort of 50–100 active daily beta testers with 20 evaluations/day quota.
