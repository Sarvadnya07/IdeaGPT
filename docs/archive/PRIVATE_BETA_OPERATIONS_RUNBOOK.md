# IdeaGPT — Private-Beta Operations Runbook

**Product**: IdeaGPT  
**Audience**: On-Call Engineers, DevOps, SREs  
**Version**: 1.0.0-rc1  

---

## 1. Daily Operations & Health Verification

### 1. Endpoint Health Probes
```bash
# 1. Process Liveness Check (Fast, unauthenticated)
curl -i https://api.ideagpt.dev/health/live
# Expected: HTTP 200 {"status": "live", "service": "IdeaGPT API"}

# 2. Database Readiness Check (Validates PostgreSQL pool)
curl -i https://api.ideagpt.dev/health/ready
# Expected: HTTP 200 {"status": "ready", "database": "connected"}

# 3. Operational Task Metrics (Requires Clerk Bearer Token)
curl -i -H "Authorization: Bearer <JWT>" https://api.ideagpt.dev/metrics
# Expected: HTTP 200 {"ai_task_metrics": {"total_tasks": ..., "by_status": {...}}}
```

---

## 2. Database Migration Runbook

Before deploying a new version with database changes:
```bash
cd apps/api

# 1. Verify 0 schema drift between models and database
python -m alembic check

# 2. Apply pending migrations
python -m alembic upgrade head

# 3. Inspect current migration head
python -m alembic current
```

---

## 3. Secret Rotation Runbook

### Groq / OpenAI API Key Rotation
1. Generate new API key in provider console.
2. Update `GROQ_API_KEY` in cloud secret manager.
3. Deploy / restart API container (`systemctl restart ideagpt-api` or ECS service update).
4. Run verification smoke test: Trigger single idea evaluation in UI.
5. Decommission old key in provider console.

### Clerk JWT Key / Domain Rotation
1. Update custom domain in Clerk Dashboard.
2. Set `CLERK_JWT_ISSUER` and `CLERK_PUBLISHABLE_KEY` in environment.
3. Verify `GET /health/config` returns `CLERK_JWT_ISSUER: explicitly_configured`.

---

## 4. Troubleshooting Guide

| Symptom | Probable Root Cause | Resolution Action |
| :--- | :--- | :--- |
| **HTTP 401 on all authenticated requests** | Clerk token issuer mismatch or expired session | Verify `CLERK_PUBLISHABLE_KEY` matches between frontend `.env.local` and backend `.env`. |
| **HTTP 503 on `/health/ready`** | Database unreachable or connection pool exhausted | Check PostgreSQL instance status; verify network security group allows port 5432. |
| **AI tasks stuck in `RUNNING` state** | Process crash during execution | Restart API pod; startup lifespan hook automatically sweeps and marks tasks older than 5m as `FAILED`. |
| **CORS error in browser console** | Origin not in backend allowlist | Add exact frontend domain to `CORS_ORIGINS` in backend environment. |
