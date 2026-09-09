# Phase A — IdeaGPT AI Gateway v1 Comprehensive Report

**Status**: Verified Production Implementation  
**Monorepo**: IdeaGPT  
**Target Milestone**: Phase A — Provider-Agnostic Capability Gateway

---

## 1. Objective

Transform the previous monolithic, Groq-centric AI implementation into a capability-oriented, provider-agnostic AI gateway serving current IdeaGPT requirements without feature bloat or modality sprawl.

---

## 2. Previous AI Architecture vs New Architecture

### Previous AI Implementation:

- Single direct provider invocation model with tightly coupled provider endpoints.
- Unstructured error bubbles and lack of capability-aware routing.
- No encrypted Bring-Your-Own-Key (BYOK) credential storage.
- External web search data conflated with generation instructions.

### New Gateway Architecture:

```
                        IDEA GPT
                           |
                      AI GATEWAY
                           |
                   CAPABILITY ROUTER
                           |
      +--------------------+--------------------+
      |                    |                    |
  GENERATION           RESEARCH            PERCEPTION
      |                    |                    |
  TEXT/REASON         WEB SEARCH          VISION/DOC
      |                    |                    |
      +--------------------+--------------------+
                           |
                   KNOWLEDGE LAYER
                    /            \
               EMBEDDING       RERANK
                (Phase A)     (future)
                           |
                     SAFETY LAYER
                           |
                   IDEA INTELLIGENCE
```

---

## 3. Capability Contracts

Located at `app/ai/gateway/contracts.py`:

- `AICapability`:
  - `TEXT_GENERATION`
  - `REASONING`
  - `STRUCTURED_OUTPUT`
  - `WEB_RESEARCH`
  - `VISION`
  - `DOCUMENT_UNDERSTANDING`
  - `EMBEDDING`
  - `MODERATION`
- `CapabilityProtocols`: Runtime-checkable Python Protocol interfaces for type safety and modular pluggability.

---

## 4. Provider Registry & Adapters

Managed via `GatewayProviderRegistry` with 60-second TTL caching to prevent outbound provider spam:

| Provider          | Type           | Primary Capabilities                                                                     | Status in Production                                                          |
| :---------------- | :------------- | :--------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------- |
| **Groq AI**       | Managed / BYOK | `TEXT_GENERATION`, `REASONING`, `STRUCTURED_OUTPUT`                                      | Operational                                                                   |
| **Google Gemini** | Managed / BYOK | `TEXT_GENERATION`, `REASONING`, `STRUCTURED_OUTPUT`, `VISION`, `DOCUMENT_UNDERSTANDING`  | Operational                                                                   |
| **Ollama**        | Local Daemon   | `TEXT_GENERATION`, `REASONING`, `STRUCTURED_OUTPUT`, `EMBEDDING`                         | Graceful Fallback (`UNAVAILABLE` when offline)                                |
| **OpenAI**        | Premium / BYOK | `TEXT_GENERATION`, `REASONING`, `STRUCTURED_OUTPUT`, `VISION`, `EMBEDDING`, `MODERATION` | Operational                                                                   |
| **Tavily AI**     | Web Research   | `WEB_RESEARCH` (Citation extraction & Source grounding)                                  | Operational                                                                   |
| **Mock Provider** | Test/Dev Only  | Test Stubs                                                                               | **STRICTLY PROHIBITED IN PRODUCTION** (`APP_ENV=production` blocks execution) |

---

## 5. Model Classification & Catalog Rules

- Conservative semantic classification ensures audio/speech-to-text models (e.g. `whisper-large-v3`) and guard models (e.g. `llama-guard-3-8b`) are strictly rejected from structured idea generation tasks (`AIInvalidModelException`).
- Dynamic discovery aggregates models from provider APIs and normalizes them into `ModelDescriptor` objects.

---

## 6. Capability-Aware Routing & Deterministic Scoring

Multi-factor candidate scoring algorithm:

1. **Capability Match**: 30%
2. **Quality & Model Family**: 20%
3. **Availability & Status**: 15%
4. **Cost / Free Tier Preference**: 10%
5. **Latency**: 10%
6. **Free Quota**: 5%
7. **User / BYOK Preference**: 5%
8. **Privacy**: 5%

### Routing Modes:

- `AUTO / AUTO`: Router dynamically selects the highest-scoring available provider and model for the task capability.
- `Explicit Provider / AUTO`: Router dynamically selects the highest-scoring model within the designated provider.
- `Explicit Provider / Explicit Model`: Router strictly honors the user's requested model if compatible with the task capability.
- `AI_UNAVAILABLE`: When no active providers are configured, returns safe normalized exception without fake responses.

---

## 7. BYOK Credential Vault & Authenticated Encryption

- **Storage**: Database table `provider_credentials` (Migration `c1d2e3f4a5b6_add_provider_credentials_table.py`).
- **Encryption**: Authenticated encryption (`Fernet` / AES-128-CBC + HMAC-SHA256) using server-side master key (`CREDENTIAL_ENCRYPTION_KEY`). Encryption keys are never written to PostgreSQL.
- **Data Privacy**: Secret API keys are accepted strictly on write; responses, logs, and frontend bundles return only non-secret masked hints (e.g., `gsk_...9a4b`).
- **Endpoints**:
  - `POST /api/v1/ai/credentials` — Store encrypted BYOK key
  - `GET /api/v1/ai/credentials` — List user's configured BYOK providers with masked hints
  - `POST /api/v1/ai/credentials/{provider}/verify` — Test live connectivity
  - `DELETE /api/v1/ai/credentials/{provider}` — Revoke and permanently purge key

---

## 8. Evidence Taxonomy & Research Grounding

- **Taxonomy**: `FACT`, `ESTIMATE`, `INFERENCE`, `RECOMMENDATION`, `UNKNOWN`.
- **Validation**:
  - Claims marked `FACT` require a verified `source_url` or `source_title`. Unsubstantiated claims are automatically downgraded to `INFERENCE`.
  - Claims marked `ESTIMATE` require documented assumptions.
- **Untrusted Input Isolation**: External web research snippets retrieved via Tavily are packaged as contextual reference data only, preventing prompt injection into system instructions.

---

## 9. Embeddings & Moderation Foundation

- `EmbeddingService`: Generates embeddings and calculates cosine similarity (`cosine_similarity`) for idea deduplication and semantic similarity.
- `ModerationService`: Input and output safety checks enforcing platform content boundaries.

---

## 10. Verification & Test Evidence

### Backend Pytest Suite:

```text
======================= 151 passed, 4 skipped in 198s =======================
```

### Frontend Vitest Suite:

```text
Test Files  5 passed (5)
     Tests  8 passed (8)
```

### Playwright E2E Suite:

```text
19 passed (31.5s)
```

### Alembic Migration Drift:

```text
python -m alembic check -> No new upgrade operations detected (0 drift).
```

### Monorepo Turbo Build:

```text
Tasks: 1 successful, 1 total (100% build success).
```
