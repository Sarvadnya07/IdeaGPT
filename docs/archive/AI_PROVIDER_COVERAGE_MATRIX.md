# 📊 AI Provider & Capability Coverage Matrix

**System**: IdeaGPT Universal AI Gateway  
**Scope**: Provider $\times$ Task Capability Mapping & Configuration Status

---

## 1. Provider Configuration Truth

| Provider ID | Provider Name           | Configured     | Enabled            | State            | Free / Dev Tier              | BYOK Supported |
| :---------- | :---------------------- | :------------- | :----------------- | :--------------- | :--------------------------- | :------------- |
| `groq`      | Groq AI (LPU Inference) | ✅ Yes         | ✅ Yes             | `AVAILABLE`      | ✅ Yes (Free Beta/On-Demand) | ✅ Yes         |
| `gemini`    | Google Gemini AI        | ❌ No          | ✅ Yes             | `NOT_CONFIGURED` | ✅ Yes (Free AI Studio Tier) | ✅ Yes         |
| `openai`    | OpenAI                  | ❌ No          | ✅ Yes             | `NOT_CONFIGURED` | ❌ Paid API Only             | ✅ Yes         |
| `ollama`    | Ollama (Local Daemon)   | ❌ No          | ✅ Yes             | `UNAVAILABLE`    | ✅ Yes (100% Free / Local)   | ❌ N/A (Local) |
| `tavily`    | Tavily Web Search       | ✅ Yes         | ✅ Yes             | `AVAILABLE`      | ✅ Yes (Free 1k Searches/Mo) | ✅ Yes         |
| `mock`      | Deterministic Test Mock | ❌ (Test Only) | ❌ (Prod Disabled) | `DISABLED`       | ❌ Test Fixture              | ❌ No          |

---

## 2. Task Capability Matrix

| Task Type                      | Required Capability      |         Groq         |         Gemini          |         OpenAI          |       Ollama       |         Tavily          |
| :----------------------------- | :----------------------- | :------------------: | :---------------------: | :---------------------: | :----------------: | :---------------------: |
| **Startup Idea Evaluation**    | `STRUCTURED_OUTPUT`      | ✅ (`gpt-oss-120b`)  | ✅ (`gemini-2.0-flash`) |      ✅ (`gpt-4o`)      |  ✅ (`llama3.2`)   |           ❌            |
| **Technology Stack**           | `STRUCTURED_OUTPUT`      | ✅ (`gpt-oss-120b`)  | ✅ (`gemini-2.0-flash`) |      ✅ (`gpt-4o`)      |  ✅ (`llama3.2`)   |           ❌            |
| **System Architecture**        | `STRUCTURED_OUTPUT`      | ✅ (`gpt-oss-120b`)  | ✅ (`gemini-2.0-flash`) |      ✅ (`gpt-4o`)      |  ✅ (`llama3.2`)   |           ❌            |
| **Product Requirements (PRD)** | `STRUCTURED_OUTPUT`      | ✅ (`gpt-oss-120b`)  | ✅ (`gemini-2.0-flash`) |      ✅ (`gpt-4o`)      |  ✅ (`llama3.2`)   |           ❌            |
| **Pitch Deck Outline**         | `STRUCTURED_OUTPUT`      | ✅ (`gpt-oss-120b`)  | ✅ (`gemini-2.0-flash`) |      ✅ (`gpt-4o`)      |  ✅ (`llama3.2`)   |           ❌            |
| **Execution Roadmap**          | `STRUCTURED_OUTPUT`      | ✅ (`gpt-oss-120b`)  | ✅ (`gemini-2.0-flash`) |      ✅ (`gpt-4o`)      |  ✅ (`llama3.2`)   |           ❌            |
| **Deep Reasoning / Strategy**  | `REASONING`              | ✅ (`gpt-oss-120b`)  |  ✅ (`gemini-1.5-pro`)  |     ✅ (`o3-mini`)      | ✅ (`deepseek-r1`) |           ❌            |
| **Web Research & Citations**   | `WEB_RESEARCH`           |          ❌          |           ❌            |           ❌            |         ❌         | ✅ (`tavily-search-v1`) |
| **Vision & UI Perception**     | `VISION`                 |          ❌          | ✅ (`gemini-2.0-flash`) |      ✅ (`gpt-4o`)      |         ❌         |           ❌            |
| **Document Understanding**     | `DOCUMENT_UNDERSTANDING` |          ❌          |  ✅ (`gemini-1.5-pro`)  |      ✅ (`gpt-4o`)      |         ❌         |           ❌            |
| **Semantic Similarity**        | `EMBEDDING`              |          ❌          |           ❌            | ✅ (`text-embedding-3`) | ✅ (`nomic-embed`) |           ❌            |
| **Content Moderation**         | `MODERATION`             | ✅ (`llama-guard-3`) |           ❌            |           ❌            |         ❌         |           ❌            |
