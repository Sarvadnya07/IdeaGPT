# IdeaGPT — Deployment Troubleshooting Guide

## Common Deployment Issues & Root-Cause Remediation

### 1. `ModuleNotFoundError: No module named 'fastapi'`
- **Cause**: Vercel deployed from a subdirectory (e.g. `apps/api`) containing a `package.json`, causing Vercel to run `pnpm install` instead of installing Python dependencies.
- **Remediation**: Set Root Directory to `.` and ensure root `requirements.txt` and `api/index.py` exist.

---

### 2. Frontend HTTP 500 (`Internal Server Error`)
- **Cause**: Missing `CLERK_SECRET_KEY` in Vercel project environment variables. Clerk's server middleware (`clerkMiddleware`) crashes during SSR without it.
- **Remediation**: Add `CLERK_SECRET_KEY` (`sk_live_...` or `sk_test_...`) to Vercel Environment Variables and redeploy without build cache.

---

### 3. FastAPI Readiness Fails (`503 Service Unavailable`)
- **Cause**: `DATABASE_URL` is unreachable, using synchronous `psycopg2` URL syntax, or using an unsupported protocol.
- **Remediation**: Ensure `DATABASE_URL` is formatted as `postgresql+asyncpg://...` (Supabase transaction pooler or direct connection with SSL enabled).

---

### 4. CORS Error when Calling Backend API
- **Cause**: `CORS_ORIGINS` in Vercel environment variables does not include the frontend deployment domain.
- **Remediation**: Update `CORS_ORIGINS` to `https://your-domain.vercel.app` (or comma-separated list of custom domains).
