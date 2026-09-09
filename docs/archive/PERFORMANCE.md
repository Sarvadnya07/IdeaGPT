# Performance Optimizations

IdeaGPT requires handling long-running asynchronous tasks (LLM inferences) while providing a snappy, premium user experience. We utilize several strategies across the stack to ensure optimal performance.

## Frontend Optimizations (Next.js)

1. **React Server Components (RSC):**
   By utilizing the Next.js App Router, heavy components are rendered on the server. This drastically reduces the JavaScript bundle size shipped to the client, improving Time to Interactive (TTI).

2. **Edge Network Caching:**
   Static pages (like the landing page) are cached on the edge (e.g., Vercel's Edge Network), providing sub-100ms response times globally.

3. **Optimistic UI Updates:**
   Using **Zustand** and **TanStack React Query**, the UI responds instantly to user inputs (like navigating the dashboard) while background fetches occur, preventing UI blocking.

4. **Animation Performance:**
   **Framer Motion** is configured to utilize hardware-accelerated CSS transforms (`transform`, `opacity`) instead of animating layout properties (`width`, `margin`), ensuring smooth 60FPS micro-animations on the frontend.

## Backend Optimizations (FastAPI)

1. **Asynchronous Architecture:**
   The entire FastAPI application is built using `async/await`. This means that when the API calls an external LLM (which can take 5-15 seconds), the thread is not blocked and can handle thousands of other incoming requests simultaneously.

2. **Pydantic V2:**
   IdeaGPT utilizes Pydantic V2, which is rewritten in Rust, providing a 5-50x speedup in schema validation and JSON serialization compared to V1.

3. **Connection Pooling:**
   Any HTTP clients used within the backend (e.g., `httpx` for calling LLMs or external services) maintain persistent connection pools rather than establishing new TLS handshakes per request.

## Monorepo Build Performance

1. **Turborepo Caching:**
   Turborepo caches build outputs (`.next/`, TypeScript compilations). If a package hasn't changed, Turbo instantly restores the output from the cache instead of rebuilding, reducing CI/CD times by up to 80%.

## Bottlenecks & Scaling Strategy

- **Current Bottleneck:** External LLM Inference speed. We cannot control how fast OpenAI/Anthropic responds.
- **Solution/Strategy:** We must implement WebSockets or Server-Sent Events (SSE) in the future to stream the LLM response back to the Next.js client token-by-token. This drastically reduces the perceived waiting time for the user.
