# 💾 AI Generated Data Persistence & Storage Architecture Report

**System**: IdeaGPT Universal AI Gateway  
**Scope**: Authoritative PostgreSQL Persistence, Relational Boundaries, Cache Invalidation Recovery & Ownership

---

## 1. Storage Hierarchy & Rules of Truth

```text
                         GENERATED DATA
                              │
               ┌──────────────┴──────────────┐
               │                             │
        STRUCTURED RESULT              LARGE ARTIFACT
               │                             │
               ▼                             ▼
         PostgreSQL                    Object Storage
          JSON/JSONB                  S3 / R2 / GCS
               │                             │
               └──────────────┬──────────────┘
                              │
                         API / UI
                              │
                         Redis CACHE
                       (never source of truth)
```

1. **PostgreSQL (`ai_artifacts`, `evaluations`, `roadmaps`) = Authoritative Application Truth**.
2. **Redis = Ephemeral Cache & Multi-Tenant Rate Limiting Only** (never authoritative).
3. **Local Filesystem = Ephemeral Runtime Only** (no permanent state stored locally).
4. **React / Browser State = Ephemeral Display Layer** (must always reload from server).

---

## 2. AI Artifact Persistence Matrix

| Feature / Generator         | Table                      | Primary Key | Foreign Keys                       | Durable Storage Format            | Reload Endpoint                 |
| :-------------------------- | :------------------------- | :---------- | :--------------------------------- | :-------------------------------- | :------------------------------ |
| **Startup Evaluation**      | `evaluations`              | `id` (UUID) | `project_id`, `idea_id`            | PostgreSQL JSON `result_payload`  | `GET /api/v1/evaluations/{id}`  |
| **Technology Stack**        | `ai_artifacts`             | `id` (UUID) | `user_id`, `project_id`, `idea_id` | PostgreSQL JSON `content_payload` | `GET /api/v1/ai/artifacts/{id}` |
| **System Architecture**     | `ai_artifacts`             | `id` (UUID) | `user_id`, `project_id`, `idea_id` | PostgreSQL JSON `content_payload` | `GET /api/v1/ai/artifacts/{id}` |
| **PRD**                     | `ai_artifacts`             | `id` (UUID) | `user_id`, `project_id`, `idea_id` | PostgreSQL JSON `content_payload` | `GET /api/v1/ai/artifacts/{id}` |
| **Pitch Deck**              | `ai_artifacts`             | `id` (UUID) | `user_id`, `project_id`, `idea_id` | PostgreSQL JSON `content_payload` | `GET /api/v1/ai/artifacts/{id}` |
| **Roadmap**                 | `ai_artifacts`, `roadmaps` | `id` (UUID) | `user_id`, `project_id`, `idea_id` | PostgreSQL JSON `content_payload` | `GET /api/v1/ai/artifacts/{id}` |
| **GitHub Scaffolding**      | `ai_artifacts`             | `id` (UUID) | `user_id`, `project_id`, `idea_id` | PostgreSQL JSON `content_payload` | `GET /api/v1/ai/artifacts/{id}` |
| **Investor Lab**            | `ai_artifacts`             | `id` (UUID) | `user_id`, `project_id`, `idea_id` | PostgreSQL JSON `content_payload` | `GET /api/v1/ai/artifacts/{id}` |
| **Mentor Lab**              | `ai_artifacts`             | `id` (UUID) | `user_id`, `project_id`, `idea_id` | PostgreSQL JSON `content_payload` | `GET /api/v1/ai/artifacts/{id}` |
| **Recruiter Lab**           | `ai_artifacts`             | `id` (UUID) | `user_id`, `project_id`, `idea_id` | PostgreSQL JSON `content_payload` | `GET /api/v1/ai/artifacts/{id}` |
| **Strategy Lab**            | `ai_artifacts`             | `id` (UUID) | `user_id`, `project_id`, `idea_id` | PostgreSQL JSON `content_payload` | `GET /api/v1/ai/artifacts/{id}` |
| **Grounded Market Dossier** | `ai_artifacts`             | `id` (UUID) | `user_id`, `project_id`, `idea_id` | PostgreSQL JSON `content_payload` | `GET /api/v1/ai/artifacts/{id}` |

---

## 3. Resilience & Invalidation Guarantees

- **Browser Refresh**: UI fetches `/api/v1/ai/artifacts/by-project/{id}` or `/evaluations/{id}` to restore complete state.
- **Backend Restart**: PostgreSQL stores all records; zero data lost on server restarts.
- **Cache Eviction / Flush**: Redis flush only forces a clean database read; results remain 100% intact.
- **Tenant Isolation**: SQL query filters `WHERE user_id = current_user.id` prevent any cross-tenant data access.
