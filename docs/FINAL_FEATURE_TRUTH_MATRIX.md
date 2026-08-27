# IdeaGPT Production Feature Truth Matrix

**Last Audit**: Phase A AI Gateway Release  
**Status**: Authoritative & Evidence-Backed  

| Component / Feature | Tier / Type | Implementation State | Verification Method |
| :--- | :--- | :--- | :--- |
| **AI Gateway v1** | Gateway Architecture | **VERIFIED & OPERATIONAL** | 20 Gateway Unit & Integration Tests |
| **Capability Router** | Multi-factor Routing | **VERIFIED & OPERATIONAL** | Deterministic Scoring & AUTO/Explicit Routing Tests |
| **Groq Adapter** | Provider Adapter | **VERIFIED & OPERATIONAL** | Dynamic Model Discovery & Structured Output Tests |
| **Google Gemini Adapter** | Provider Adapter | **VERIFIED & OPERATIONAL** | Model Discovery, Vision & Document Contract Tests |
| **Ollama Adapter** | Local Provider | **VERIFIED & OPERATIONAL** | Offline Graceful State & Local Invocation Tests |
| **OpenAI Adapter** | Premium Provider | **VERIFIED & OPERATIONAL** | BYOK Model Discovery & Schema Generation Tests |
| **Tavily Research Provider** | Web Research | **VERIFIED & OPERATIONAL** | Citation Extraction & Source Normalization Tests |
| **BYOK Credential Vault** | Security & Privacy | **VERIFIED & OPERATIONAL** | AES Encryption, Tenant Isolation & Masked Key Tests |
| **Evidence Taxonomy** | Fact/Estimate System | **VERIFIED & OPERATIONAL** | Source Enforcement & Downgrade Validator Tests |
| **Embeddings & Similarity** | Vector Knowledge | **VERIFIED & OPERATIONAL** | Cosine Similarity & Vector Normalization Tests |
| **Moderation Boundary** | Safety | **VERIFIED & OPERATIONAL** | Heuristic Policy & Keyword Guard Tests |
| **Mock Provider Rule** | Testing Isolation | **VERIFIED & ENFORCED** | Strictly Disabled in Production (`APP_ENV=production`) |
| **Clerk Authentication** | Identity | **VERIFIED & OPERATIONAL** | RS256 JWKS & Playwright Protected Route Tests |
| **Deterministic Engine** | Core Evaluation | **VERIFIED & OPERATIONAL** | 100% Deterministic Fallback Coverage |
| **Roadmap Generation** | AI Analysis Lab | **VERIFIED & OPERATIONAL** | CRUD, Status Toggle, AI Generation Tests |
| **Analytics Dashboard** | Observability | **VERIFIED & OPERATIONAL** | User-Scoped DB-Driven Aggregation Tests |
