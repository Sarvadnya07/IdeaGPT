# IdeaGPT Production Feature Truth Matrix

**Last Audit**: Universal AI Provider Usage, Free-Tier Coverage, Persistence & Runtime Truth Release  
**Status**: Authoritative & Evidence-Backed  

| Component / Feature | Tier / Type | Implementation State | Verification Method |
| :--- | :--- | :--- | :--- |
| **Universal AI Gateway v1** | Gateway Architecture | **VERIFIED & OPERATIONAL** | 220 Backend Tests & Fast Discovery Benchmark |
| **Capability Router & Allowlist** | Multi-factor Routing | **VERIFIED & OPERATIONAL** | Deterministic Allowlist & Model Capability Tests |
| **Model Quarantine State Machine** | Resilience | **VERIFIED & OPERATIONAL** | 404/403 Instant Model Eviction Tests |
| **Durable AI Artifact Persistence** | PostgreSQL Storage | **VERIFIED & OPERATIONAL** | `ai_artifacts` table migration & Tenant Isolation Tests |
| **Groq LPU Provider** | Free / Dev Tier Inference | **VERIFIED & OPERATIONAL** | `openai/gpt-oss-120b` live inference & test coverage |
| **Tavily Research Provider** | Web Research | **VERIFIED & OPERATIONAL** | Citation Extraction & SSRF Defense Tests |
| **BYOK Credential Vault** | Security & Privacy | **VERIFIED & OPERATIONAL** | Fernet Symmetric Encryption & Tenant Isolation Tests |
| **SSRF Defense Layer** | Security Boundary | **VERIFIED & OPERATIONAL** | Loopback, RFC1918 & Cloud Metadata Blocking Tests |
| **FinOps Cost & Admission Control** | Budget Guardrails | **VERIFIED & OPERATIONAL** | Token-Aware Admission & Cost Ceilings Tests |
| **Circuit Breaker & Bulkheads** | Resilience | **VERIFIED & OPERATIONAL** | Tripping, Cooldown, and Concurrency Tests |
| **Content Sanitization** | XSS Defense | **VERIFIED & OPERATIONAL** | Markdown / HTML Tag & Event Stripping Tests |
| **Phase B Evidence Layer** | Grounded Research | **VERIFIED & OPERATIONAL** | 12 Grounded Research & Mira Benchmark Tests |
| **Phase C Deep Reasoning** | Decision Intelligence | **VERIFIED & OPERATIONAL** | 11 Reasoning, Contradiction & Metamorphic Tests |
| **Assumption Priority Engine** | Decision Science | **VERIFIED & OPERATIONAL** | Discrete Normalized Formula Math Tests |
| **What-If Scenario Simulator** | Operational Modeling | **VERIFIED & OPERATIONAL** | Deterministic Runway & Perturbation Tests |
| **Single-Variable Sensitivity** | Elasticity Analysis | **VERIFIED & OPERATIONAL** | Baseline vs Perturbed Elasticity Tests |
| **Multi-Idea Comparative Strategy** | Comparative Modeling| **VERIFIED & OPERATIONAL** | Weighted Criteria & Risk-Adjusted Scoring Tests |
| **Strategy -> Roadmap Linkage** | Execution Bridge | **VERIFIED & OPERATIONAL** | PostgreSQL / SQLite Roadmap Persistence Tests |
| **Strategy Lab Workspace** (`/strategy-lab`) | Core UI | **VERIFIED & OPERATIONAL** | 5 Vitest Component Tests & Playwright E2E |
| **Multi-Idea Compare** (`/compare`) | Core UI | **VERIFIED & OPERATIONAL** | Playwright Route & Form Testing |
| **Clerk Authentication** | Identity | **VERIFIED & OPERATIONAL** | RS256 JWKS & Playwright Protected Route Tests |
| **Deterministic Engine** | Core Evaluation | **VERIFIED & OPERATIONAL** | 100% Deterministic Fallback Coverage |
| **Full Backend Regression** | Reliability | **VERIFIED & OPERATIONAL** | 220 Passed, 4 Skipped, 0 Failures |
