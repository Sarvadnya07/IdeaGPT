# ⚡ AI Gateway Reliability & Provider Resilience Report

**System**: IdeaGPT Universal AI Gateway  
**Scope**: Fault Tolerance, Timeouts, Retry Budgets, Circuit Breakers, Bulkheads & Graceful Degradation  
**Status**: VERIFIED & PRODUCTION READY  

---

## 1. Reliability Architecture

The IdeaGPT AI Gateway treats all AI providers (Groq, Gemini, OpenAI, Ollama, Tavily) as untrusted, potentially failing external dependencies.

```text
Incoming Task
     │
     ▼
[Bulkhead Concurrency Gate]
     │
     ▼
[Circuit Breaker Check] ──(OPEN)──> Fallback / Return Clean 503
     │ (CLOSED / HALF_OPEN)
     ▼
[Token-Aware Admission Reservation]
     │
     ▼
[Bounded HTTP Dispatch with Timeouts (5s connect / 30s read)]
     │
     ├─► Success: Record circuit success, reconcile tokens, return AIResult
     │
     └─► 429/503/Timeout: Bounded Exponential Jittered Retry (max 2 attempts)
           │
           └─► Persistent Failure: Trip Circuit Breaker, failover to secondary provider if policy permits
```

---

## 2. Timeouts & Retry Budgets

### Explicit Network Timeouts
- **Connect Timeout**: `5.0s` across all provider adapters.
- **Read / Generation Timeout**: `15.0s` for web research, `30.0s` for complex LLM reasoning.
- **Total Request Deadline**: Enforced at HTTP and background task executor boundaries.

### Bounded Retry Strategy
- **Retryable Statuses**: `429 (Rate Limit)`, `503 (Service Unavailable)`, `504 (Gateway Timeout)`, `httpx.TimeoutException`.
- **Non-Retryable Statuses**: `400 (Bad Request)`, `401/403 (Auth/Permissions)`, `422 (Schema Error)`, `Safety Refusals`. Non-retryable errors abort immediately without wasting upstream tokens.
- **Backoff & Jitter**: Full jitter exponential backoff with respect for upstream `Retry-After` headers.

---

## 3. Circuit Breaker State Machine

Each provider maintains an independent `ProviderCircuitBreaker`:

| State | Transition Condition | Allowed Behavior |
| :--- | :--- | :--- |
| **CLOSED** | Initial / Healthy. Resets upon successful calls. | All requests dispatched normally. |
| **OPEN** | $\ge 5$ consecutive fatal provider failures. | Dispatches blocked immediately; requests fail fast or route to fallback. |
| **HALF_OPEN**| Cooldown period (30s) elapses. | Single canary probe dispatched to test vendor health. |

---

## 4. Concurrency Bulkheads

Isolated `asyncio.Semaphore` pools prevent resource exhaustion in one workload domain from impacting others:

- **Interactive Requests** (Chat / Live Tools): Concurrency ceiling = 20
- **Background AI Tasks** (Asynchronous Evaluations): Concurrency ceiling = 10
- **Web Research Jobs** (Tavily Searches): Concurrency ceiling = 5
- **Embeddings & Vector Processing**: Concurrency ceiling = 15

---

## 5. Graceful Degradation & Zero-AI Mode

When external AI providers are unavailable:
- **AI-Dependent Tasks**: Return normalized `AI_UNAVAILABLE` error payloads with safe retryable guidance.
- **Deterministic Features**: Evaluation score computation, rule validation, project/idea CRUD, financial formulas, and scenario simulations run strictly on deterministic algorithmic engines without failing.
