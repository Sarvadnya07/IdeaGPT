# 🎯 IdeaGPT AI Gateway — Threat Model & Attack Surface Analysis

**System**: IdeaGPT Universal AI Gateway  
**Methodology**: STRIDE / OWASP Top 10 for LLM Applications  
**Status**: AUDITED & REMEDIATED  

---

## 1. Threat Vectors & Deterministic Mitigations

```text
┌─────────────────────────┬──────────────────────────────────┬────────────────────────────────────────────────────────┐
│ Threat Category         │ Attack Scenario                  │ Deterministic Application Mitigation                   │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. Secret Exfiltration  │ Malicious user / log inspection  │ Fernet encryption at rest, masked key hints, error      │
│                         │ attempts to steal provider keys  │ redaction, zero secret exposure in API responses.       │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 2. Cross-Tenant Breach  │ User B reads/deletes User A's    │ Strict SQL user_id tenancy predicates on all vault,     │
│                         │ BYOK credentials or AI tasks     │ task, and cache operations. 404 returned on tampering. │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 3. Model Spoofing       │ Client injects arbitrary/costly  │ Server-side model allowlist & capability matrix in     │
│                         │ model IDs (e.g. gpt-5-custom)    │ CapabilityRouter. Immediate 400 rejection.             │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 4. SSRF & Metadata Steal│ Web research or URL fetcher is   │ Pre-flight DNS resolution, private RFC1918 blocking,   │
│                         │ pointed to 169.254.169.254 / LAN │ cloud metadata blocking, non-HTTP scheme rejection.    │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 5. Prompt & Data Inject │ Malicious user prompt attempts   │ Explicit <untrusted_user_input> and                    │
│                         │ to override system instructions  │ <untrusted_research_data> boundary envelopes.          │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 6. Output XSS Injection │ LLM returns Markdown with        │ ContentSanitizer strips scripts, dangerous link        │
│                         │ <script> or javascript: links    │ protocols, iframes, and onerror event handlers.        │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 7. Denial of Wallet     │ Runaway token loop or infinite   │ Hard single-request ($0.25) and user daily ($2.00)     │
│    (Cost Abuse)         │ retry chain drains budget        │ cost ceilings with pre-flight token admission tickets. │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 8. Cascading Outage     │ Upstream AI provider goes down   │ Per-provider circuit breaker trips to OPEN after 5     │
│                         │ causing worker pool starvation   │ failures; isolated concurrency bulkheads protect apps. │
├─────────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 9. Unbounded Tools      │ Autonomous tool loops run        │ ToolPolicyEngine enforces strict 5-step / 8-call max,  │
│                         │ arbitrary commands or recursion  │ $0.50 cost cap, 30s wall clock, and allowed tool list. │
└─────────────────────────┴──────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. OWASP LLM Top 10 Compliance Matrix

| OWASP LLM Category | Description | IdeaGPT Status | Verification Reference |
| :--- | :--- | :--- | :--- |
| **LLM01: Prompt Injection** | Untrusted content hijacking model intent | ✅ MITIGATED | `PromptGuard` untrusted data boundaries |
| **LLM02: Sensitive Info Disclosure** | Model revealing API keys / system secrets | ✅ MITIGATED | `CredentialVaultService` encryption & redaction |
| **LLM03: Supply Chain Vulnerabilities** | Compromised models or providers | ✅ MITIGATED | `CapabilityRouter` strict allowlist & checksums |
| **LLM04: Data & Model Poisoning** | Malicious retrieved evidence | ✅ MITIGATED | Evidence scoring, confidence thresholds, citations |
| **LLM05: Improper Output Handling** | XSS / HTML injection in UI | ✅ MITIGATED | `ContentSanitizer` regex & DOM stripping |
| **LLM06: Excessive Agency** | Autonomous tool over-reach | ✅ MITIGATED | `ToolPolicyEngine` least-privilege tool whitelist |
| **LLM07: System Prompt Leakage** | Extraction of internal system prompts | ✅ MITIGATED | Separated role envelopes, schema-only outputs |
| **LLM08: Vector & Embedding Weaknesses** | Cross-tenant vector similarity poisoning | ✅ MITIGATED | User & project tenancy scoping on embeddings |
| **LLM09: Misinformation** | Hallucinated facts and claims | ✅ MITIGATED | Multi-source grounded evidence normalization |
| **LLM10: Unbounded Consumption** | Resource exhaustion / DoS / billing spike | ✅ MITIGATED | Token admission, cost ceilings, circuit breaker |
