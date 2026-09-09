# IdeaGPT — Final Runtime Truth & Provider Matrix

## Provider Runtime Verification Status

| Provider | Enabled Default | Live Health Verification | Capability Matrix | Dynamic Discovery | BYOK Support | Runtime Classification |
|---|---|---|---|---|---|---|
| **Groq (Primary LPU)** | Yes | Live discovery & latency probe (<500ms) | TEXT_GEN, STRUCTURED_OUTPUT, REASONING | Active via `/openai/v1/models` | Supported | **VERIFIED & OPERATIONAL** |
| **Gemini (Multimodal)** | Optional (Config dependent) | Live probe & SDK check | TEXT_GEN, STRUCTURED_OUTPUT, VISION, DOC_UNDERSTANDING | Active | Supported | **CONFIGURED / READY** |
| **OpenAI / Compatible** | Optional (Config dependent) | Live ping probe | TEXT_GEN, STRUCTURED_OUTPUT, REASONING, EMBEDDING | Active | Supported | **CONFIGURED / READY** |
| **Ollama (Local Private)**| Optional (Config dependent) | Local endpoint probe (`11434`) | TEXT_GEN, STRUCTURED_OUTPUT | Active | Supported | **CONFIGURED / READY** |
| **Tavily (Deep Research)**| Optional (Config dependent) | Live search test | WEB_RESEARCH | Active | Supported | **CONFIGURED / READY** |
| **Deterministic Engine** | Built-in Baseline | Native in-process execution (<5ms) | FULL_SUITE_COMPUTATION | Active (No external dependency) | N/A | **ACTIVE & VERIFIED** |
| **Mock Engine (Testing)** | Test-mode Only | In-memory synchronous runner | ALL_CAPABILITIES | Isolated to test/mock mode | N/A | **TEST-MODE VERIFIED** |

## Model Allowlist Verification
- **Allowlist Enforced**: Clients cannot submit arbitrary model IDs. Spoofed or unknown models (e.g. `whisper-large-v3` for text generation or arbitrary strings) are rejected with `400 Bad Request` / `AIInvalidModelException`.
- **Dynamic Quarantine**: Models failing with upstream 404/403 or fatal errors are automatically quarantined for 300 seconds and evicted from discovery cache.
