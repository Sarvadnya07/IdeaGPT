# Future Scope & Project Roadmap

IdeaGPT has successfully established a highly robust, scalable SaaS foundation utilizing a decoupled AI Orchestrator and strict tenant isolation. As the platform evolves, the following roadmap details our short-term enhancements, long-term visions, and architectural scaling strategies.

## 🚀 Short-Term Improvements (Next 1-3 Months)

1. **AI Evaluation UI (Sprint 4)**
   - Implement the multi-step Idea Submission form.
   - Build a real-time polling or WebSocket interface for the AI Background Tasks (`Queued -> Processing -> Completed`).
   - Auto-redirect to a dynamic Analysis Results dashboard upon completion.

2. **Rate Limiting & Security Hardening**
   - Implement `slowapi` on the FastAPI backend to throttle abusive IP requests and protect AI API budgets.
   - Restrict project creation volume based on user tier/subscription status.

3. **LLM Provider Expansion**
   - Flesh out the `GeminiProvider` and `OllamaProvider` interfaces within the `AIOrchestrator` registry to allow users to select their preferred inference engine.

## 🌟 Long-Term Roadmap (6-12 Months)

1. **Automated Roadmaps & Tech Stack Recommendations**
   - Expand the AI Pipeline to dynamically generate Gantt charts and exact CI/CD/Cloud infrastructure blueprints based on the Idea Context.

2. **Investor Pitch Deck Generator**
   - Utilize AI to automatically extrapolate the evaluation data into a downloadable, slides-based PDF format.

3. **GitHub Codebase Initializer**
   - Integrate with GitHub API to automatically bootstrap a repository containing the exact recommended Tech Stack boilerplate.

## 📈 Scalability Strategies

As traffic scales, the current single-instance FastAPI setup and localized background tasks will bottleneck.

1. **Message Queues (Celery + Redis)**
   - **Current State:** AI requests are processed via FastAPI `BackgroundTasks`, running in the same memory space as the web server.
   - **Future State:** Delegate AI inference payloads to a distributed Celery worker pool orchestrated by Redis, allowing independent scaling of Web Nodes and AI Workers.

2. **Database Pooling (PgBouncer)**
   - Implement PgBouncer at the network edge to multiplex PostgreSQL connections across thousands of concurrent lambda/serverless connections.

3. **CDN Caching**
   - Heavily cache static `get_user_projects` responses at the Cloudflare edge to minimize database reads, triggering invalidation only on `POST/PATCH` mutations.
