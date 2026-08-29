# ⚠️ AI Runtime Failure & Root-Cause Remediation Report

**System**: IdeaGPT Universal AI Gateway  
**Scope**: Model 404/403 Diagnosis, Timeout Alignment, Error Normalization, and Safe Fallback  

---

## 1. Observed Runtime Incidents & Root Causes

### Incident 1: Serial 404/403 Cascade on Groq
- **Symptom**: Model discovery and execution logged:
  - `Groq candidate model 'llama-3.3-70b-versatile' unavailable: Error code: 404 - model_not_found`
  - `Groq candidate model 'qwen/qwen3.8-27b' unavailable: Error code: 403 - model_permission_blocked_project`
- **Root Cause**: The active Groq organization/project tier did not have permissions enabled for `qwen/qwen3.8-27b` and did not list `llama-3.3-70b-versatile`. Serial attempts across 5 candidates wasted 12+ seconds.
- **Remediation**:
  1. `GroqProviderAdapter` prioritized working `openai/gpt-oss-120b`.
  2. Implemented `gateway_registry.quarantine_model(model_id, duration_sec=300)` on 404/403 errors, instantly evicting failing candidates from the router pool.

### Incident 2: Model Discovery Cold-Start Latency (~15.7s)
- **Symptom**: `GET /api/v1/ai/models` took 15.7 seconds on cold start.
- **Root Cause**: Adapters were queried serially; offline/unconfigured adapters waited for connection timeouts.
- **Remediation**:
  1. Replaced serial loop with concurrent `asyncio.gather` and 2.5s per-adapter deadlines.
  2. Added static pre-populated baseline descriptors for instant (<10ms) responses.
  3. Stale-While-Revalidate (SWR) cache pattern.

### Incident 3: Frontend Axios 10s Timeout Mismatch
- **Symptom**: Complex PRD and Architecture generation requests took ~12 seconds on the backend, returning HTTP 200, but the frontend aborted at 10.0 seconds with `ECONNABORTED`.
- **Root Cause**: Hardcoded `timeout: 10000` in `apps/web/lib/api/client.ts`.
- **Remediation**: Increased Axios timeout to `45000` (45 seconds), fully aligning client wait times with backend generation SLAs.
