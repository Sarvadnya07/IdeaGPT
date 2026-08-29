# IdeaGPT — Production Observability & Telemetry Status

**Product**: IdeaGPT  
**Auditor**: Principal Observability & SRE Lead  
**Assessment Date**: August 2026  

---

## 1. Observability Architecture

```text
[HTTP Request]
       │
       ├── Ingest 'x-request-id' or generate UUIDv4 (sanitized alphanumeric <= 64 chars)
       ├── Attach request_id to request.state and response headers
       ├── Process request through middleware pipeline
       ├── Output structured JSON log to stdout:
       │     {
       │       "timestamp": "2026-08-30T00:15:00Z",
       │       "level": "INFO",
       │       "request_id": "req-98f24a18-...",
       │       "method": "POST",
       │       "url": "/api/v1/ai/tasks",
       │       "path": "/api/v1/ai/tasks",
       │       "status_code": 200,
       │       "process_time_ms": 24.5,
       │       "client_ip": "192.168.1.10"
       │     }
       └── Query scrubbing: Sensitive URL parameters automatically redacted
```

---

## 2. Health & Operational Telemetry Endpoints

| Endpoint | Auth Required | Purpose | Response |
| :--- | :---: | :--- | :--- |
| `GET /health` | No | Basic heartbeat check | `{"status": "healthy", "service": "IdeaGPT API"}` |
| `GET /health/live` | No | Kubernetes / ECS Liveness Probe (process up, no DB dependency) | `{"status": "live"}` |
| `GET /health/ready` | No | Kubernetes / ECS Readiness Probe (validates DB connectivity) | `{"status": "ready", "database": "connected"}` or `503` |
| `GET /health/config` | Yes (Clerk) | Validates environment configuration status without exposing secret values | `{"APP_ENV": "production", "CLERK_PUBLISHABLE_KEY": "configured", ...}` |
| `GET /health/providers` | Yes (Clerk) | Real-time status of configured AI providers | `{"groq": "available", "openai": "available", ...}` |
| `GET /metrics` | Yes (Clerk) | AI task state metrics (total count, breakdown by `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`) | `{"ai_task_metrics": {"total_tasks": 142, "by_status": {...}}}` |

---

## 3. Telemetry Invariants & Log Privacy

1. **Zero Secret Logging**: JWT tokens, authorization headers, raw API keys, and database passwords are strictly excluded from logs.
2. **Correlation Header Propagation**: All responses include the standard `x-request-id` header for end-to-end user request debugging.
3. **Structured Format**: Formatted as single-line JSON strings to facilitate streaming ingestion into Datadog, AWS CloudWatch, Grafana Loki, or Google Cloud Logging.
