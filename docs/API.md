# 🌐 IdeaGPT REST API Specification & Guide

The IdeaGPT API is built on FastAPI and acts as the core intelligence and domain orchestration engine.

---

## 📍 Base URL & Interactive Documentation

* **Base URL:** `http://localhost:8000/api/v1`
* **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Specification:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **OpenAPI Schema (JSON):** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 🔒 Authentication & Authorization

All authenticated endpoints require an RS256 JWT issued by Clerk passed in the `Authorization` header:

```http
Authorization: Bearer <clerk_jwt_token>
```

### Authentication Lifecycle:
1. **Verification:** FastAPI verifies the token's RS256 signature against Clerk's public JWKS (`PyJWKClient`).
2. **User Synchronization:** The `sub` claim is extracted. `get_current_user` retrieves or creates the user in the PostgreSQL `users` table.
3. **Tenant Scoping:** All operations (`Project`, `Idea`, `Evaluation`) are scoped strictly to `current_user.id`. Client-provided `user_id` fields are never trusted.

---

## 📦 Core Endpoint Catalog

### 1. Health & Configuration
* `GET /health` — Service readiness and uptime status.
* `GET /health/ai` — Active AI provider and fallback status.
* `GET /health/providers` — Health check across configured LLM providers (Groq, OpenAI, Gemini, Ollama).
* `GET /health/config` — Non-secret environment configuration state.

### 2. User Domain (`/api/v1/users`)
* `GET /api/v1/users/me` — Retrieve current authenticated user profile.
* `PATCH /api/v1/users/me` — Update user profile metadata (name, timezone, avatar).

### 3. Project Domain (`/api/v1/projects`)
* `POST /api/v1/projects/` — Create a new project workspace.
* `GET /api/v1/projects/` — List projects (supports `search`, `category`, `is_pinned`, `is_archived`, pagination).
* `GET /api/v1/projects/{project_id}` — Retrieve project by ID.
* `PATCH /api/v1/projects/{project_id}` — Update project metadata.
* `PATCH /api/v1/projects/{project_id}/pin` — Toggle pinned status.
* `PATCH /api/v1/projects/{project_id}/archive` — Toggle archived status.
* `POST /api/v1/projects/{project_id}/duplicate` — Duplicate project + clone active ideas.
* `DELETE /api/v1/projects/{project_id}` — Soft delete project (`deleted_at = now()`).

### 4. Idea Domain (`/api/v1`)
* `POST /api/v1/projects/{project_id}/ideas` — Create idea under owned project.
* `GET /api/v1/projects/{project_id}/ideas` — List ideas under owned project.
* `GET /api/v1/ideas/{idea_id}` — Retrieve idea details.
* `PATCH /api/v1/ideas/{idea_id}` — Update idea content (mutable fields).
* `POST /api/v1/ideas/{idea_id}/duplicate` — Duplicate idea (starts as draft).
* `DELETE /api/v1/ideas/{idea_id}` — Hard delete idea row from PostgreSQL.

### 5. Evaluation & AI Gateway (`/api/v1/evaluations`)
* `POST /api/v1/ideas/{idea_id}/evaluations` — Trigger multi-dimensional AI evaluation.
* `GET /api/v1/evaluations/{evaluation_id}` — Retrieve evaluation payload and score metrics.
* `GET /api/v1/search?q={query}` — Global search scoped to current user's projects.

---

## 🛡️ Error Contract

Errors return structured JSON following RFC-7807 standards:

```json
{
  "detail": "Descriptive error message"
}
```

* **401 Unauthorized:** Missing, expired, or invalid Clerk JWT.
* **403 Forbidden:** Unauthorized tenant access attempt.
* **404 Not Found:** Resource does not exist or is owned by another tenant.
* **422 Unprocessable Entity:** Schema validation error (e.g. invalid string length or type).
* **429 Too Many Requests:** Rate limit exceeded via `slowapi`.
