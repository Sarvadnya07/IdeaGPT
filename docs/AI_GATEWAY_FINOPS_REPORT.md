# 💰 AI Gateway FinOps & Cost Control Report

**System**: IdeaGPT Universal AI Gateway  
**Scope**: Token-Aware Admission, Cost Ceilings, Multi-Tier Rate Limiting & Spend Tracking  
**Status**: VERIFIED & PRODUCTION READY  

---

## 1. Multi-Dimensional FinOps Guardrails

```text
                  Incoming AI Request
                          │
                          ▼
            [1. Token & Cost Estimation]
              (input_tokens + max_output_tokens)
                          │
                          ▼
            [2. Per-Request Max Ceiling] ──(> $0.25)──► REJECT (CostLimitException)
                          │ (<= $0.25)
                          ▼
            [3. User Daily Budget Check] ──(> $2.00)──► REJECT (CostLimitException)
                          │ (<= $2.00)
                          ▼
            [4. Threshold Policy Engine]
              • < 50%: ALLOW (Standard dispatch)
              • >= 50%: WARN (Log advisory)
              • >= 70%: THROTTLE (Apply concurrency wait)
              • >= 80%: DOWNGRADE (Route to 8B Instant model)
              • >= 90%: REJECT (Preserve critical budget)
                          │
                          ▼
            [5. Admission Ticket Issued (Reserve)]
                          │
                          ▼
                 [Provider Execution]
                          │
                          ▼
            [6. Usage Reconciliation & Release]
```

---

## 2. Hard Cost Ceilings

| Guardrail Parameter | Limit | Enforcement Mechanism |
| :--- | :--- | :--- |
| **Max Single-Request Spend** | **$0.25 USD** | Pre-flight token calculation check |
| **Max Per-User Daily Spend** | **$2.00 USD** | Cumulative 24-hour spend aggregation |
| **Max Per-Tenant Monthly Spend** | **$50.00 USD** | Cumulative billing cycle aggregation |
| **Max Input Prompt Length** | **8,000 characters** | String length validation before tokenization |
| **Max Concurrent Tasks / User** | **3 tasks** | Database active task count check |
| **Max Daily Tasks / User** | **20 tasks** | Daily task creation counter |

---

## 3. Provider Cost Modeling (Per 1k Tokens)

| Provider / Family | Model ID | Input Cost ($/1k) | Output Cost ($/1k) | Default Tier |
| :--- | :--- | :--- | :--- | :--- |
| **Groq** | `llama-3.3-70b-versatile` | $0.00059 | $0.00079 | Primary Workhorse |
| **Groq** | `llama-3.1-8b-instant` | $0.00005 | $0.00008 | Fast / Summary / Downgrade |
| **Gemini** | `gemini-2.0-flash` | $0.00010 | $0.00040 | Vision / Perception |
| **Gemini** | `gemini-1.5-pro` | $0.00125 | $0.00500 | Deep Reasoning (BYOK / Premium) |
| **OpenAI** | `gpt-4o` | $0.00250 | $0.01000 | BYOK Fallback |
| **OpenAI** | `gpt-4o-mini` | $0.00015 | $0.00060 | BYOK Lightweight |
| **Ollama** | Local Models | $0.00000 | $0.00000 | Self-Hosted / On-Prem |

---

## 4. Token-Aware Admission & Reconciliation Protocol

1. **Pre-Flight Estimation**: Input token count is computed via length heuristics ($char / 4$) or BPE tokenizer; output tokens are bounded by `max_output_tokens`.
2. **Reservation**: `AdmissionController` issues a ticket reserving the estimated cost against user and tenant quotas.
3. **Execution**: The provider executes the prompt and returns precise `prompt_tokens` and `completion_tokens` in normalized `AIUsage`.
4. **Reconciliation**: `AdmissionController.reconcile_ticket` computes exact cost, releases surplus reservation back to the pool, and updates analytics tables.
