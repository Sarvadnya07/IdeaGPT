# IdeaGPT — Production FinOps & Cost Governance Status

**Product**: IdeaGPT  
**Auditor**: Principal FinOps Engineer  
**Assessment Date**: August 2026  

---

## 1. Inference Cost & Quota Controls

```text
[Incoming Evaluation Request]
        │
        ├── 1. Length Validation: Prompt <= 8,000 chars (prevents token overflow)
        │
        ├── 2. SlowAPI Rate Limit: 5 evaluations / minute / user
        │
        ├── 3. Database Daily Quota: 20 evaluations / day / user (free tier ceiling)
        │
        ├── 4. Capability Scoring: Selects lowest-cost capable model (Groq LPU priority)
        │
        └── 5. Token Telemetry: Records execution duration, model, and provider used
```

---

## 2. FinOps Policy Matrix

| Policy Dimension | Configuration / Bound | Purpose |
| :--- | :--- | :--- |
| **Max Prompt Length** | 8,000 characters | Prevents multi-megabyte payloads from consuming excessive context window tokens. |
| **User Daily Quota** | 20 evaluations / day | Prevents runaway automated scripts or single users draining monthly LLM spend. |
| **Burst Limiting** | 5 requests / min (`AI_EVALUATION_RATE_LIMIT`) | Prevents rapid concurrent parallel generation storms. |
| **Preferred Tier** | Groq Llama 3.3 70B Versatile | Extremely cost-effective token pricing (~$0.59 / 1M tokens) vs high-cost proprietary frontier models. |
| **Fallback Preference** | Gemini 2.0 Flash / OpenAI GPT-4o-mini | Routes to economical fallback tiers before escalating to expensive models. |
| **Model Caching** | 60-second TTL | Prevents continuous billable discovery queries to provider management APIs. |

---

## 3. Cost Runway Projections (Private Beta)

- **Beta Cohort Size**: 50 active daily users
- **Max Theoretical Daily Tasks**: 50 users × 20 evaluations = 1,000 evaluations / day
- **Average Tokens per Evaluation**: ~1,500 input + 1,200 output = 2,700 tokens
- **Estimated Daily Token Volume**: ~2.7 Million tokens / day
- **Estimated Daily Inference Spend (Groq LPU)**: **~$1.60 / day** ($48.00 / month)
- **FinOps Verdict**: 🟢 **SAFE FOR PRIVATE BETA DEPLOYMENT**
