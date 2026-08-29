# 🆓 Free AI Provider Verification Report

**System**: IdeaGPT Universal AI Gateway  
**Scope**: Free-Tier & Local AI Provider Integration Verification  

---

## 1. Verified Free-Tier & Local Providers

| Provider | Model ID | Status | Capabilities Tested | Latency | Cost |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Groq (Free/On-Demand)** | `openai/gpt-oss-120b` | ✅ ACTIVE | Text Generation, Reasoning, Structured JSON | ~1200ms | $0.00 (On-Demand Tier) |
| **Groq (Fast Tier)** | `llama-3.1-8b-instant` | ✅ ACTIVE | Fast Summaries, Keyword Extraction | ~450ms | $0.00 (On-Demand Tier) |
| **Tavily (Free Dev Tier)**| `tavily-search-v1` | ✅ ACTIVE | Grounded Web Search & Evidence Extraction | ~950ms | $0.00 (Free 1k/Mo API) |
| **Google Gemini (AI Studio)**| `gemini-2.0-flash` | ⚠️ Ready for Key | Vision, Documents, Structured Output | N/A | Free RPM Quota |
| **Ollama (Local AI)** | `llama3.2` / `deepseek-r1` | ⚠️ Ready for Daemon | 100% Local Offline Inference | N/A | $0.00 |

---

## 2. Dynamic Discovery & Failover Rules

1. **Free Workhorse**: Groq `openai/gpt-oss-120b` handles all structured evaluations, PRD, architecture, and roadmaps without subscription cost.
2. **Free Downgrade**: If daily tokens approach threshold (80%+), the gateway automatically downgrades non-critical summaries to `llama-3.1-8b-instant`.
3. **Local Privacy**: When Ollama daemon is detected on `localhost:11434`, users can route sensitive ideas entirely offline with zero data leaving the server.
