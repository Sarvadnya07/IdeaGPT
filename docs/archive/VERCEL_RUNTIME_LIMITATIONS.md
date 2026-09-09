# IdeaGPT — Vercel Runtime Limitations & Constraints

## Serverless Constraints & Mitigations

1. **Function Execution Timeouts**:
   - Vercel Serverless Functions have maximum execution limits (15s on Hobby, 60s/300s on Pro/Fluid Compute).
   - *Mitigation*: AI task endpoints return `202 Accepted` with an `id`, execute bounded AI inferences, and stream progress via SSE (`/api/v1/ai/tasks/{id}/stream`) with a 30-second cap.
2. **Stateless Instances & In-Memory State**:
   - In-memory process dictionaries are not shared across serverless instances.
   - *Mitigation*: All evaluations, AI artifacts, roadmaps, and tasks are strictly persisted in PostgreSQL.
3. **Database Connection Scaling**:
   - High concurrency serverless spikes can exhaust direct database connection limits.
   - *Mitigation*: Dynamic serverless connection pool (`DB_POOL_SIZE=5`), connection recycling, and Supabase / Supavisor shared pooler on port 5432 / 6543.
4. **Local Daemon Processes (Ollama / Local Celery)**:
   - Localhost services (e.g. `http://localhost:11434` for Ollama) do not exist in Vercel cloud environments.
   - *Mitigation*: Vercel backend relies on cloud providers (Groq, Gemini, OpenAI) and deterministic engine fallbacks.
