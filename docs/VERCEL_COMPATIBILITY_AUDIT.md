# IdeaGPT — Vercel Compatibility & Eligibility Audit

## Forensic Evaluation Summary

| Subsystem | Vercel Eligibility | Notes & Implementation |
|---|---|---|
| **Next.js 16 (Turbopack)** | Fully Compatible | 21 routes statically / dynamically optimized. React 19 SSR and Client components. |
| **FastAPI 0.136** | Fully Compatible | ASGI application mounted via `apps/api/index.py` for `@vercel/python`. |
| **SQLAlchemy 2.0 (Async)** | Compatible with Adaptations | Dynamic serverless connection pooling (`DB_POOL_SIZE=5`) prevents PostgreSQL connection exhaustion. |
| **Alembic Migrations** | External / CI/CD Only | Migrations must not run inside short-lived serverless invocations; run via GitHub Actions or manual CLI (`alembic upgrade head`). |
| **AI Task Lifecycle** | Fully Compatible | All task states (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`) persist to PostgreSQL. Stale tasks recovered on boot. |
| **Streaming / SSE** | Fully Compatible | Native `StreamingResponse` (text/event-stream) with `X-Accel-Buffering: no` supported. |
| **WebSockets** | Not Applicable | REST and SSE are used exclusively. |
| **Redis** | Optional / Graceful Fallback | Rate limiting and in-process background tasks operate with local fallback if external Redis is absent. |
| **Filesystem** | Ephemeral / Safe | Ephemeral `/tmp` usage only; all durable assets persist to PostgreSQL (`ai_artifacts`). |
