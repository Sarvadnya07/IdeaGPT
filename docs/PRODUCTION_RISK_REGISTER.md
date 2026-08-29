# IdeaGPT — Production Risk Register

**Last Updated**: August 2026  
**Auditor**: Principal SRE & Security Engineer  

---

## 1. Risk Register & Mitigation Matrix

| Risk ID | Risk Description | Severity | Category | Mitigation in Repository | Operational Requirement | Status |
| :--- | :--- | :---: | :---: | :--- | :--- | :---: |
| **RSK-01** | Clerk RS256 token verification failure | **P0** | Auth | Installed `cryptography==44.0.2` in `requirements.txt` and verified PyJWKClient. | Configure production `CLERK_PUBLISHABLE_KEY` | 🟢 **FIXED IN CODE** |
| **RSK-02** | Database connection pool exhaustion during long AI inference | **P1** | Database | Configured `pool_size=20`, `max_overflow=10`, `pool_recycle=300`, `pool_timeout=30`. | Size DB instance (e.g. AWS RDS db.t4g.medium) | 🟢 **FIXED IN CODE** |
| **RSK-03** | Stale background tasks stuck in `RUNNING` after pod restarts | **P1** | Reliability | Dual startup sweeps in `lifespan` for `Evaluation` and `AiTask` (5-min timeout transition to `FAILED`). | Enable container liveness/readiness probes | 🟢 **FIXED IN CODE** |
| **RSK-04** | Prompt injection or adversarial instruction override | **P1** | AI Safety | System prompts isolate user context into tagged delimiters with structured JSON repair schemas. | Review prompt templates on new LLM versions | 🟢 **FIXED IN CODE** |
| **RSK-05** | Rate limit and quota bypass via parallel tab requests | **P1** | FinOps | Enforced `SlowAPI` token bucket limiting (`5/min` for evaluations, `30/min` for write API) + DB-backed daily user quotas. | Optional Redis cluster storage for distributed instances | 🟢 **FIXED IN CODE** |
| **RSK-06** | Cross-tenant data access (IDOR / data leakage) | **P0** | Security | All queries enforce `user_id == current_user.id` at ORM level with 403/404 rejection on unauthorized access. | Maintain strict test security matrices | 🟢 **FIXED IN CODE** |
| **RSK-07** | Stale Groq model name deprecation | **P2** | AI Gateway | Dynamic model discovery with 60-second TTL cache + conservative capability classifier. | Maintain Groq Cloud billing / API key validity | 🟢 **FIXED IN CODE** |
| **RSK-08** | Sensitive query parameters / token leakage in logs | **P2** | Compliance | URL query scrubber `_sanitize_url` redacts `token`, `secret`, `key`, `password` before stdout logging. | Centralized log ingestion (Datadog / CloudWatch) | 🟢 **FIXED IN CODE** |
| **RSK-09** | Database disaster recovery & data loss | **P1** | Infrastructure | ACID transactional rollback on session failure. | Configure automated daily snapshots & 7-day PITR | 🟡 **REQUIRES INFRASTRUCTURE** |
| **RSK-10** | Clerk custom production domain & SSO | **P2** | Auth | Backend supports explicit `CLERK_JWT_ISSUER` and `CLERK_AUTHORIZED_PARTY`. | Set up custom domain in Clerk Dashboard | 🟡 **REQUIRES EXTERNAL CONFIGURATION** |

---

## 2. Risk Scoring & Summary

- **Total Assessed Risks**: 10
- **Mitigated & Fixed in Code**: 8 (80%)
- **Infrastructure / Operational Prerequisites**: 2 (20%)
- **Active Unmitigated Blockers**: **0**
