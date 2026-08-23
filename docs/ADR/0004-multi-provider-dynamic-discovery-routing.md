# 4. Multi-Provider Dynamic Discovery & AI Routing

Date: 2026-08-17

## Status
Accepted

## Context
Deploying LLM capabilities across multiple external providers (Groq, OpenAI, Gemini, Ollama) requires avoiding single-vendor lock-in, adapting to new model releases dynamically, and handling provider outages with automatic fallback routing.

## Decision
We implemented `AIRouter` and `AIRegistryService` featuring:
1. **Dynamic Model Discovery**: Queries provider model catalogs with a 60-second TTL in-memory cache to discover available models without redeploying code.
2. **Conservative Capability Classification**: Categorizes models by capabilities (`TEXT_GENERATION`, `STRUCTURED_OUTPUT`, `SPEECH_TO_TEXT`, `MODERATION`), filtering out non-text models from evaluation pipelines.
3. **Deterministic Ranking & Fallbacks**: Prioritizes production-ready high-throughput models (e.g. Groq Llama 3.3 70B Versatile / Llama 3.1 8B Instant) while failing over gracefully to OpenAI/Gemini/Ollama or Mock providers.
4. **Asynchronous Task Queue & Streaming**: Idempotent AI tasks executed via background workers with Server-Sent Events (SSE) streaming support.

## Consequences
### Pros:
- Complete independence from any single AI vendor.
- Immediate zero-code support when providers add new models.
- Graceful degraded operation during external API outages.
- Reduced API bill through intelligent model tier routing.

### Cons:
- Multiple vendor SDK interfaces must be maintained in provider adaptors.
