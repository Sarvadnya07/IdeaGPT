# API Guide

The IdeaGPT API is built on FastAPI and serves as the core intelligence layer. It adheres to RESTful principles and uses JSON for request and response payloads.

## Base URL

When running locally, the API is available at:
`http://localhost:8000/api/v1`

## Endpoints

### 1. Health Check

Checks if the API service is active and responsive.

**Request:**
`GET /`

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "IdeaGPT API"
}
```

---

### 2. Submit Project Idea

Analyzes a user's startup idea and generates a technical roadmap and evaluation.

**Request:**
`POST /api/v1/projects/submit`

**Headers:**

- `Content-Type: application/json`
- `Authorization: Bearer <token>` (If authentication is enabled)

**Body (`ProjectCreate` Schema):**

```json
{
  "idea_description": "An AI-powered application that generates marketing copy for real estate agents.",
  "target_audience": "Real Estate Agents, Brokers",
  "budget_level": "medium"
}
```

**Response (200 OK):**

```json
{
  "project_id": "uuid-1234",
  "analysis": {
    "technical_complexity": "Moderate",
    "estimated_timeline_weeks": 8,
    "architecture_recommendation": {
      "frontend": "Next.js",
      "backend": "Node.js or Python",
      "database": "PostgreSQL"
    },
    "key_risks": [
      "AI Hallucinations in generated copy",
      "Integration with MLS databases"
    ]
  }
}
```

**Error Responses:**

- **422 Unprocessable Entity:** Payload failed validation (e.g., missing `idea_description`).
- **500 Internal Server Error:** LLM service timeout or failure.

## Authentication

Authentication (when implemented) will use JWT (JSON Web Tokens).
Include the token in the `Authorization` header:
`Authorization: Bearer YOUR_ACCESS_TOKEN`

## Error Handling

FastAPI automatically handles schema validation errors and returns a `422 Unprocessable Entity` with a detailed breakdown of which fields failed.

Custom application errors will follow this structure:

```json
{
  "detail": "Descriptive error message",
  "error_code": "SPECIFIC_ERROR_CODE"
}
```

## Swagger Documentation

FastAPI automatically generates interactive OpenAPI documentation. You can explore and test the endpoints directly from your browser when the server is running:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
