# 🛡️ AI Gateway Security Hardening Report

**System**: IdeaGPT Universal AI Gateway  
**Audit & Remediation Scope**: P0–P3 Deterministic Security Controls (Phases 0–60)  
**Status**: VERIFIED & PRODUCTION READY  

---

## 1. Executive Summary & Security Philosophy

The IdeaGPT AI Gateway enforces a deterministic defense-in-depth model where:
```text
MODEL = UNTRUSTED
PROVIDER = UNTRUSTED EXTERNAL DEPENDENCY
APPLICATION = FINAL AUTHORITY
```

Deterministic guarantees are enforced in application code before LLM dispatch, during execution, and after result generation. Security is never left to prompt engineering alone.

```text
       SYSTEM POLICY
            >
      DEVELOPER POLICY
            >
         USER INPUT
            >
       RETRIEVED DATA
            >
        TOOL OUTPUT
            >
        MODEL OUTPUT
```

---

## 2. P0 Security Controls & Verification

### 2.1 Secrets & BYOK Encryption at Rest
- **Mechanism**: Fernet-authenticated symmetric encryption (`AES-128-CBC` with `HMAC-SHA256`) using key derivation from master secret.
- **Exposure Boundary**: Plaintext API keys are **never** returned in API responses, task payloads, logs, or exceptions.
- **Key Hint**: Keys are masked using non-secret prefixes and suffixes (`gsk_...9a4b`).
- **Lifecycle**: Full state machine (`NEW` $\to$ `VERIFIED` $\to$ `ACTIVE` $\to$ `REVOKED`). Revocation immediately blocks future key retrieval.
- **Verification**: Verified in `tests/test_ai_gateway_security_hardening.py::test_byok_encryption_envelope_and_masking`.

### 2.2 Cross-Tenant Isolation
- **Tenant Scope**: All BYOK credentials, AI tasks, token usage, rate limits, budgets, cache entries, and evidence vectors are scoped strictly by `user_id`.
- **Zero Cross-Talk**: User B cannot query, verify, use, or delete User A's stored credentials or execution records.
- **Verification**: Verified in `tests/test_ai_gateway_security_hardening.py::test_byok_cross_user_tenant_isolation_matrix`.

### 2.3 Server-Side Model Allowlist & Capability Enforcement
- **Model Allowlist**: `CapabilityRouter` validates requested model strings against `PROVIDER_MODEL_ALLOWLIST`.
- **Arbitrary Model Rejection**: Any arbitrary, retired, or unrecognized model ID is rejected with `400 AIInvalidModelException`.
- **Capability Matrix**: Models lacking task-required capabilities (e.g. Speech-to-Text models for structured evaluation, or Moderation guards for generation) are rejected.
- **Verification**: Verified in `tests/test_ai_gateway_security_hardening.py::test_model_allowlist_rejects_arbitrary_client_models`.

### 2.4 Server-Side Request Forgery (SSRF) Defense
- **Pre-Flight DNS & Network Resolution**: `SSRFGuard` checks URL syntax, resolves DNS pre-flight, and rejects:
  - Loopback (`127.0.0.1/8`, `::1`)
  - Cloud metadata (`169.254.169.254`, `metadata.google.internal`, `100.100.100.200`)
  - RFC 1918 Private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
  - Unsafe schemes (`file://`, `gopher://`, `ftp://`, `dict://`)
  - NAT64 translation checking
- **Redirect Security**: Redirect chains are bounded to 3 hops with post-redirect IP validation.
- **Verification**: Verified in `tests/test_ai_gateway_security_hardening.py::test_ssrf_blocks_loopback_and_localhost` through `test_ssrf_allows_legitimate_public_urls`.

---

## 3. P1 & P2 Controls: Sanitization, Prompt Isolation, Tools & Circuit Breakers

### 3.1 Content Sanitization & XSS Defense
- `ContentSanitizer` neutralizes `<script>` tags, `javascript:` / `data:` URI links, unsafe `<iframe>` elements, and HTML event handlers (`onerror=`, `onclick=`) from LLM outputs.

### 3.2 Prompt & Research Untrusted Envelopes
- `PromptGuard` explicitly encloses user input and retrieved web research snippets in `<untrusted_user_input>` and `<untrusted_research_data>` envelopes. System instructions instruct the model that data within envelopes cannot alter evaluation rules or schemas.

### 3.3 Tool Policy & Budgets
- `ToolPolicyEngine` validates tool permissions against `ALLOWED_TOOLS` and enforces deterministic execution budgets:
  - `max_steps`: 5
  - `max_tool_calls`: 8
  - `max_wall_clock_sec`: 30.0s
  - `max_tokens`: 8192
  - `max_cost_usd`: $0.50
  - `max_recursion_depth`: 2

### 3.4 Circuit Breaker & Concurrency Bulkheads
- `ProviderCircuitBreaker` manages `CLOSED` $\to$ `OPEN` $\to$ `HALF_OPEN` states. 5 sustained provider failures trip the breaker, preventing cascade failure storms.
- `WorkloadBulkhead` isolates concurrency pools across interactive requests, background AI tasks, research jobs, and embeddings.

---

## 4. Test Evidence Summary

| Security Test Domain | Test File | Status |
| :--- | :--- | :--- |
| BYOK Secret Encryption & Masking | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
| BYOK Cross-Tenant Isolation | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
| BYOK Credential Lifecycle & Revocation | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
| Server-Side Model Allowlist | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
| Capability Incompatibility Checks | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
| SSRF Loopback & Localhost Defense | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
| SSRF Cloud Metadata Defense | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
| SSRF RFC 1918 Private IP Defense | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
| SSRF Scheme & Redirect Bounding | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
| XSS Output Sanitization | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
| Prompt & Research Envelopes | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
| Tool Policy & Budget Caps | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
| Provider Error Sanitization | `test_ai_gateway_security_hardening.py` | ✅ PASSED |
