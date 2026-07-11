# Security Considerations

Security is paramount for IdeaGPT, especially since the platform processes proprietary startup ideas and integrates with third-party Large Language Models (LLMs).

## Security Architecture

1. **Decoupled Key Management:** 
   The Next.js frontend NEVER communicates directly with OpenAI, Anthropic, or any LLM provider. This prevents API keys from being leaked to the client bundle. All LLM requests are proxied securely through the FastAPI backend (`apps/api`).

2. **CORS Configuration:**
   The FastAPI backend explicitly defines allowed origins (`CORS_ORIGINS`). In production, this must strictly be limited to the exact domain of the Next.js frontend (e.g., `https://ideagpt.com`), preventing Cross-Origin Resource Sharing attacks.

3. **Input Sanitization & Schema Validation:**
   Before any data touches the LLM prompt or database, it is rigorously validated using Pydantic in FastAPI. This mitigates prompt injection attacks and standard injection vectors (SQLi, XSS). Pydantic ensures only expected types and lengths are processed.

## Sensitive Configuration Handling

- **Never Commit `.env`:** Ensure `.env` and `.env.local` remain in `.gitignore`.
- **Secret Management in CI/CD:** Use GitHub Actions Secrets or Vercel/Render Environment Variables to inject secrets during build/deployment, never hardcoding them.
- **API Key Rotation:** Regularly rotate LLM API keys.

## Threat Considerations & Mitigations

### 1. Prompt Injection
*Risk:* Users attempting to trick the LLM into revealing internal system prompts or performing unintended actions.
*Mitigation:* The backend utilizes strict prompt templates where user input is treated as string variables, not executable instructions. Pydantic limits input lengths to prevent exhaustive payload attacks.

### 2. Rate Limiting (DDoS / Cost Exhaustion)
*Risk:* Malicious users spamming the `submit` endpoint, running up massive LLM API bills.
*Mitigation:* (Future Implementation) FastAPI should utilize a rate-limiting middleware (e.g., `slowapi`) keyed by IP address or authenticated User ID.

### 3. Data Privacy
*Risk:* Storing sensitive, unreleased startup intellectual property (IP).
*Mitigation:* Ensure any databases (when implemented) encrypt data at rest. LLM providers should be configured for zero-data-retention (e.g., using OpenAI's API which does not train on API data by default).

## Best Practices for Contributors

- Run `npm audit` or `pnpm audit` regularly to check for vulnerable JS dependencies.
- Use `safety check` in Python to scan `requirements.txt` for known vulnerabilities.
- Review all new packages before adding them to the workspace.
