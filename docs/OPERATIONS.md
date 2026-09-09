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
