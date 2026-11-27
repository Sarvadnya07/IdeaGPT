# ⚙️ IdeaGPT Production Operations & Runbook

This runbook provides guidance for monitoring, health verification, observability, and incident recovery for IdeaGPT.

---

## 🩺 Health Check Endpoints

IdeaGPT exposes four dedicated health diagnostic routes:

| Endpoint | Purpose | Healthy Response | Failure Indication |
| :--- | :--- | :--- | :--- |
| `GET /health` | Basic API liveness | `{"status": "healthy", "service": "IdeaGPT API"}` | 500 / Network Timeout |
| `GET /health/ai` | AI Gateway status | `{"status": "healthy", "default_provider": "groq", ...}` | AI provider degraded |
| `GET /health/providers` | Provider connectivity | `{"groq": "healthy", "openai": "missing_key", ...}` | Provider API failure |
| `GET /health/config` | Non-secret config state | `{"APP_ENV": "production", "CLERK_JWT_ISSUER": "configured", ...}` | Missing required config |

---

## 🗄️ Database Operations

### Running Migrations
Alembic manages all schema migrations. Always verify drift before deployment:

```bash
# Check current migration revision
cd apps/api
node run-python.js -m alembic current

# Check if model changes require a new migration
node run-python.js -m alembic check

# Apply pending migrations
node run-python.js -m alembic upgrade head
```

### Local PostgreSQL Disaster Recovery & Reset
If local Docker database state becomes corrupted:

```bash
# Stop containers and remove volumes
pnpm db:down -v

# Start fresh containers
pnpm db:up

# Run migrations
pnpm db:migrate
```

---

## 📊 Observability & Logging

* **Structured Logging:** FastAPI outputs structured JSON logs with UTC timestamps, HTTP method, path, response status, and request duration in milliseconds.
* **Sensitive Data Redaction:** Headers containing `Authorization`, API keys, and secret credentials are automatically stripped from log traces.
* **Prometheus Metrics:** `GET /metrics` (authenticated via `METRICS_SCRAPE_TOKEN` or Clerk JWT) returns standard Prometheus text exposition (`text/plain; version=0.0.4`).

---

## 💾 Production Backup, Restore & Disaster Recovery

* **Automated Backups:** Managed PostgreSQL daily automated snapshots + WAL archiving (or `pg_dump --format=custom --no-owner`).
* **Restore Verification Gate:** A backup is not considered valid until restored into an isolated database and verified with `alembic current` + `SELECT count(*) FROM users;`.
* **Pre-Deploy Migration Gate:** Run `alembic upgrade head` in a pre-deploy step against a recent snapshot; verify zero lock contention (`CONCURRENTLY` for index builds) before rolling application traffic.

---

## 🚨 Incident Response Runbooks

1. **Database Unavailable (`/health/ready` returns 503):** Check `GET /health/db-diagnostics` (authenticated) for `failure_class`, verify PostgreSQL pool saturation (`DB_POOL_SIZE` / `DB_STATEMENT_TIMEOUT_MS`), and check managed DB health.
2. **AI Provider Outage / Circuit Open:** `CircuitBreakerRegistry` opens automatically after repeated failures and routes evaluations to `DeterministicFallback`. Inspect `GET /ops/health-monitor` and `GET /health/providers`.
3. **Bad Deployment / Rollback:** Roll back Vercel deployment to previous immutable build and redeploy previous Railway Docker image; if a schema migration is non-reversible, execute roll-forward hotfix migration.
