# IdeaGPT REST API Endpoints Specification

Base URL: `http://localhost:8000/api/v1` (or production configured host)  
Authentication: RFC 6750 Bearer Tokens (`Authorization: Bearer <clerk_session_jwt>`)

---

## 1. System Health & Observability

| Method | Path | Summary | Auth Required | Description |
| :--- | :--- | :--- | :---: | :--- |
| `GET` | `/` or `/health` | Service Ping | No | Basic API service health confirmation. |
| `GET` | `/health/live` | Process Liveness | No | Fast probe verifying process is responsive. |
| `GET` | `/health/ready` | Database Readiness | No | Verifies active PostgreSQL database connectivity. |
| `GET` | `/health/config` | Security State | No | Non-sensitive diagnostic report of security config. |
| `GET` | `/health/ai` | AI Health Status | No | Status of enabled AI providers and default engine. |
| `GET` | `/health/providers`| Provider Health | No | Detailed health status per configured AI provider. |
| `GET` | `/metrics` | Operational Metrics | No | Returns database AI task status distributions. |

---

## 2. User & Workspace Projects

| Method | Path | Summary | Auth Required | Description |
| :--- | :--- | :--- | :---: | :--- |
| `GET` | `/api/v1/users/me` | Current User | Yes | Returns or auto-synchronizes authenticated user record. |
| `GET` | `/api/v1/projects` | List Projects | Yes | Returns paginated list of user-owned projects. |
| `POST` | `/api/v1/projects` | Create Project | Yes | Creates a new workspace project domain. |
| `GET` | `/api/v1/projects/{id}` | Get Project | Yes | Retrieves project details and verifies user ownership. |
| `PUT` | `/api/v1/projects/{id}` | Update Project | Yes | Updates project title, description, category, tags. |
| `DELETE`| `/api/v1/projects/{id}`| Delete Project | Yes | Soft-deletes project and associated child ideas. |

---

## 3. Idea Capture & Evaluation Engine

| Method | Path | Summary | Auth Required | Description |
| :--- | :--- | :--- | :---: | :--- |
| `POST` | `/api/v1/projects/{id}/ideas` | Create Idea | Yes | Submits a structured idea to a project domain. |
| `GET` | `/api/v1/projects/{id}/ideas` | List Ideas | Yes | Lists all ideas within a user-owned project. |
| `GET` | `/api/v1/ideas/{id}` | Get Idea | Yes | Retrieves idea record and verifies ownership. |
| `PUT` | `/api/v1/ideas/{id}` | Update Idea | Yes | Updates idea title, problem, solution, notes. |
| `DELETE`| `/api/v1/ideas/{id}` | Delete Idea | Yes | Deletes an idea and cascading evaluations. |
| `POST` | `/api/v1/ideas/{id}/evaluations` | Run Evaluation | Yes | Triggers deterministic evaluation engine ($<50$ms). |
| `GET` | `/api/v1/evaluations/{id}` | Get Evaluation | Yes | Retrieves evaluation report and dimensional scores. |
| `GET` | `/api/v1/evaluations/{id}/history` | Audit Trail | Yes | Returns immutable lifecycle state transition log. |
| `POST` | `/api/v1/evaluations/{id}/retry` | Retry Job | Yes | Retries a FAILED or CANCELLED evaluation. |
| `POST` | `/api/v1/evaluations/{id}/cancel`| Cancel Job | Yes | Cancels an active in-flight evaluation. |
| `POST` | `/api/v1/evaluations/compare` | Compare Ideas | Yes | Side-by-side benchmark matrix of 2–5 ideas. |
| `POST` | `/api/v1/exports/json` | Export JSON | Yes | Exports evaluation payload as raw JSON. |
| `POST` | `/api/v1/exports/markdown` | Export Markdown | Yes | Exports evaluation payload as Markdown. |

---

## 4. Product Roadmaps

| Method | Path | Summary | Auth Required | Description |
| :--- | :--- | :--- | :---: | :--- |
| `GET` | `/api/v1/projects/{id}/roadmaps` | Get Roadmap | Yes | Retrieves or bootstraps project roadmap milestones. |
| `PUT` | `/api/v1/roadmaps/{id}` | Update Roadmap | Yes | Updates milestone timeline, tasks, and completion state. |

---

## 5. AI Intelligence Tools & Task Streaming

| Method | Path | Summary | Auth Required | Description |
| :--- | :--- | :--- | :---: | :--- |
| `POST` | `/api/v1/ai/tech-stack` | Tech Stack | Yes | Tailored 5-layer tech stack recommendations. |
| `POST` | `/api/v1/ai/architecture` | System Blueprint | Yes | System topology, Mermaid flow, and DB entity models. |
| `POST` | `/api/v1/ai/prd` | PRD Generator | Yes | Automated Product Requirements Document with KPIs. |
| `POST` | `/api/v1/ai/pitch-deck` | Pitch Deck | Yes | 10-slide VC presentation outline. |
| `GET` | `/api/v1/ai/providers` | List Providers | No | Returns registered AI providers and status. |
| `GET` | `/api/v1/ai/models` | List Models | No | Returns dynamic model catalog (60s TTL cache). |
| `POST` | `/api/v1/ai/tasks` | Create AI Task | Yes | Enqueues async LLM task with idempotency (HTTP 202). |
| `GET` | `/api/v1/ai/tasks/{id}` | Get AI Task | Yes | Polls AI task execution status and output payload. |
| `GET` | `/api/v1/ai/tasks/{id}/stream` | Stream AI Task | Yes | **Server-Sent Events (SSE)** real-time stream (`text/event-stream`). |

---

## 6. Analytics & Global Search

| Method | Path | Summary | Auth Required | Description |
| :--- | :--- | :--- | :---: | :--- |
| `GET` | `/api/v1/analytics` | Analytics Data | Yes | Time-series metrics, score distributions, project counts. |
| `GET` | `/api/v1/search` | Global Search | Yes | Full-text search across ideas and evaluations. |
