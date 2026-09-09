# IdeaGPT — Final Production Risk Register

## Risk Assessment & Mitigation Matrix

| Risk ID | Risk Description | Likelihood | Impact | Severity | Implemented Mitigation | Residual Risk | Status |
|---|---|---|---|---|---|---|---|
| **RSK-01** | Production Misconfiguration (SQLite / Wildcard CORS) | Low | High | Medium | Lifespan fail-fast validation in `app/main.py` halts startup immediately on unsafe config. | Negligible | **MITIGATED** |
| **RSK-02** | Upstream AI Provider Outage / Flakiness | Medium | High | High | Dynamic capability scoring, per-provider circuit breakers, and automatic deterministic fallback engine. | Low | **MITIGATED** |
| **RSK-03** | Prompt Injection & Malicious Research Content | Medium | High | High | `PromptGuard` envelope boundary isolation and strict `ContentSanitizer` for Markdown/HTML output. | Low | **MITIGATED** |
| **RSK-04** | SSRF via External URL Fetching / Web Research | Low | Critical | High | `SSRFGuard` with private IP network blocking, DNS pre-flight verification, redirect hopping bounds, and size limits. | Negligible | **MITIGATED** |
| **RSK-05** | API Key Theft / Unencrypted Secrets | Low | Critical | High | Fernet AES encryption in `CredentialVaultService` with masked key hints for all BYOK providers. | Negligible | **MITIGATED** |
| **RSK-06** | Financial Runaway / Uncontrolled AI Spend | Medium | High | Medium | `CostGuardrails` enforcing per-request ceilings ($0.25), daily budgets ($2.00), and monthly tenant limits ($50.00). | Low | **MITIGATED** |
| **RSK-07** | Stale / Zombie Background AI Tasks | Medium | Medium | Medium | Automated startup & periodic sweeper in `EvaluationCoordinator` and `AiTaskService` recovering stale jobs. | Negligible | **MITIGATED** |
