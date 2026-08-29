# IdeaGPT REST API Endpoints Specification

Base URL: `http://localhost:8000/api/v1` (or production configured host)  
Authentication: RFC 6750 Bearer Tokens (`Authorization: Bearer <clerk_session_jwt>`)

---

## 1. System Health & Observability

| Method | Path                | Summary             | Auth Required | Description                                         |
| :----- | :------------------ | :------------------ | :-----------: | :-------------------------------------------------- |
| `GET`  | `/` or `/health`    | Service Ping        |      No       | Basic API service health confirmation.              |
| `GET`  | `/health/live`      | Process Liveness    |      No       | Fast probe verifying process is responsive.         |
| `GET`  | `/health/ready`     | Database Readiness  |      No       | Verifies active PostgreSQL database connectivity.   |
| `GET`  | `/health/config`    | Security State      |      No       | Non-sensitive diagnostic report of security config. |
| `GET`  | `/health/ai`        | AI Health Status    |      No       | Status of enabled AI providers and default engine.  |
| `GET`  | `/health/providers` | Provider Health     |      No       | Detailed health status per configured AI provider.  |
| `GET`  | `/metrics`          | Operational Metrics |      No       | Returns database AI task status distributions.      |

---

## 2. User & Workspace Projects

| Method   | Path                              | Summary           | Auth Required | Description                                                                      |
| :------- | :-------------------------------- | :---------------- | :-----------: | :------------------------------------------------------------------------------- |
| `GET`    | `/api/v1/users/me`                | Current User      |      Yes      | Returns or auto-synchronizes authenticated user record.                          |
| `PATCH`  | `/api/v1/users/me`                | Update User       |      Yes      | Updates profile metadata (name, username, avatar).                               |
| `GET`    | `/api/v1/projects`                | List Projects     |      Yes      | Returns paginated list of user-owned projects (`limit` bounded 1-100, `offset`). |
| `POST`   | `/api/v1/projects`                | Create Project    |      Yes      | Creates a new workspace project domain.                                          |
| `GET`    | `/api/v1/projects/{id}`           | Get Project       |      Yes      | Retrieves project details and verifies user ownership.                           |
| `PATCH`  | `/api/v1/projects/{id}`           | Update Project    |      Yes      | Updates project title, description, category, color, icon.                       |
| `PATCH`  | `/api/v1/projects/{id}/pin`       | Toggle Pin        |      Yes      | Toggles pinned status for the project.                                           |
| `PATCH`  | `/api/v1/projects/{id}/archive`   | Toggle Archive    |      Yes      | Toggles archive status for the project.                                          |
| `POST`   | `/api/v1/projects/{id}/duplicate` | Duplicate Project |      Yes      | Clones a project domain.                                                         |
| `DELETE` | `/api/v1/projects/{id}`           | Delete Project    |      Yes      | Deletes project and cascades to associated child ideas.                          |

---

## 3. Idea Capture & Evaluation Engine

| Method   | Path                                | Summary                  | Auth Required | Description                                                  |
| :------- | :---------------------------------- | :----------------------- | :-----------: | :----------------------------------------------------------- |
| `POST`   | `/api/v1/projects/{id}/ideas`       | Create Idea              |      Yes      | Submits a structured idea to a project domain.               |
| `GET`    | `/api/v1/projects/{id}/ideas`       | List Ideas               |      Yes      | Lists all ideas within a user-owned project.                 |
| `GET`    | `/api/v1/ideas/{id}`                | Get Idea                 |      Yes      | Retrieves idea record and verifies ownership.                |
| `PATCH`  | `/api/v1/ideas/{id}`                | Update Idea              |      Yes      | Updates idea title, problem, solution, notes.                |
| `DELETE` | `/api/v1/ideas/{id}`                | Delete Idea              |      Yes      | Deletes an idea and cascading evaluations.                   |
| `POST`   | `/api/v1/ideas/{id}/duplicate`      | Duplicate Idea           |      Yes      | Clones an idea within a project.                             |
| `POST`   | `/api/v1/ideas/{id}/evaluations`    | Run Evaluation           |      Yes      | Triggers evaluation engine with multi-provider fallback.     |
| `GET`    | `/api/v1/evaluations/{id}`          | Get Evaluation           |      Yes      | Retrieves evaluation report and dimensional scores.          |
| `GET`    | `/api/v1/ideas/{id}/evaluations`    | List Idea Evaluations    |      Yes      | Lists all evaluation jobs for an idea.                       |
| `GET`    | `/api/v1/projects/{id}/evaluations` | List Project Evaluations |      Yes      | Lists all evaluations across ideas in a project.             |
| `GET`    | `/api/v1/evaluations/{id}/insights` | Evaluation Insights      |      Yes      | Returns SWOT, Feasibility, and structured insights.          |
| `GET`    | `/api/v1/evaluations/{id}/scores`   | Evaluation Scores        |      Yes      | Returns multi-dimensional breakdown scores.                  |
| `GET`    | `/api/v1/evaluations/{id}/charts`   | Chart Visualization      |      Yes      | Returns radar, bar, and risk chart datasets.                 |
| `GET`    | `/api/v1/evaluations/{id}/history`  | Audit Trail              |      Yes      | Returns immutable lifecycle state transition log.            |
| `POST`   | `/api/v1/evaluations/{id}/retry`    | Retry Job                |      Yes      | Retries a FAILED or CANCELLED evaluation.                    |
| `POST`   | `/api/v1/evaluations/{id}/cancel`   | Cancel Job               |      Yes      | Cancels an active in-flight evaluation.                      |
| `DELETE` | `/api/v1/evaluations/{id}`          | Delete Evaluation        |      Yes      | Deletes an evaluation record.                                |
| `POST`   | `/api/v1/evaluations/compare`       | Compare Ideas            |      Yes      | Side-by-side benchmark matrix of 2–5 ideas.                  |
| `GET`    | `/api/v1/projects/{id}/comparisons` | Project Comparisons      |      Yes      | Comparison matrix for multiple evaluations via Query params. |
| `POST`   | `/api/v1/exports/json`              | Export JSON              |      Yes      | Exports evaluation payload as raw JSON.                      |
| `POST`   | `/api/v1/exports/markdown`          | Export Markdown          |      Yes      | Exports evaluation payload as Markdown.                      |

---

## 4. Product Roadmaps

| Method   | Path                             | Summary        | Auth Required | Description                                              |
| :------- | :------------------------------- | :------------- | :-----------: | :------------------------------------------------------- |
| `POST`   | `/api/v1/projects/{id}/roadmaps` | Create Roadmap |      Yes      | Creates milestone roadmap structure.                     |
| `GET`    | `/api/v1/projects/{id}/roadmaps` | List Roadmaps  |      Yes      | Retrieves project roadmap milestones.                    |
| `GET`    | `/api/v1/roadmaps/{id}`          | Get Roadmap    |      Yes      | Retrieves single roadmap by ID.                          |
| `PATCH`  | `/api/v1/roadmaps/{id}`          | Update Roadmap |      Yes      | Updates milestone timeline, tasks, and completion state. |
| `DELETE` | `/api/v1/roadmaps/{id}`          | Delete Roadmap |      Yes      | Deletes roadmap resource.                                |

---

## 5. AI Intelligence Tools & Task Streaming

| Method | Path                           | Summary          | Auth Required | Description                                                          |
| :----- | :----------------------------- | :--------------- | :-----------: | :------------------------------------------------------------------- |
| `POST` | `/api/v1/ai/roadmap`           | AI Roadmap Gen   |      Yes      | Generates tailored roadmap milestones from idea metadata.            |
| `POST` | `/api/v1/ai/tech-stack`        | Tech Stack       |      Yes      | Tailored 5-layer tech stack recommendations.                         |
| `POST` | `/api/v1/ai/architecture`      | System Blueprint |      Yes      | System topology, Mermaid flow, and DB entity models.                 |
| `POST` | `/api/v1/ai/prd`               | PRD Generator    |      Yes      | Automated Product Requirements Document with KPIs.                   |
| `POST` | `/api/v1/ai/pitch-deck`        | Pitch Deck       |      Yes      | 10-slide VC presentation outline.                                    |
| `GET`  | `/api/v1/ai/providers`         | List Providers   |      No       | Returns registered AI providers and status.                          |
| `GET`  | `/api/v1/ai/models`            | List Models      |      No       | Returns dynamic model catalog (60s TTL cache).                       |
| `POST` | `/api/v1/ai/registry/refresh`  | Refresh Registry |      No       | Invalidates provider and model cache.                                |
| `POST` | `/api/v1/ai/tasks`             | Create AI Task   |      Yes      | Enqueues async LLM task with idempotency (HTTP 202).                 |
| `GET`  | `/api/v1/ai/tasks/{id}`        | Get AI Task      |      Yes      | Polls AI task execution status and output payload.                   |
| `GET`  | `/api/v1/ai/tasks/{id}/stream` | Stream AI Task   |      Yes      | **Server-Sent Events (SSE)** real-time stream (`text/event-stream`). |

---

## 6. Analytics & Global Search

| Method | Path                | Summary        | Auth Required | Description                                                            |
| :----- | :------------------ | :------------- | :-----------: | :--------------------------------------------------------------------- | --- | --- | --- | ------ |
| `GET`  | `/api/v1/analytics` | Analytics Data |      Yes      | Time-series metrics, score distributions, project counts (`range=7d    | 30d | 90d | 1y  | all`). |
| `GET`  | `/api/v1/search`    | Global Search  |      Yes      | Scoped full-text search across ideas (`min_length=2`, max 10 results). |
