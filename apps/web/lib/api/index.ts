/**
 * Unauthenticated base axios instance.
 *
 * ⚠️  WARNING: This client does NOT attach a Clerk Bearer token.
 * Do NOT use this client for any protected API endpoints.
 *
 * For authenticated requests, import and use the `useApiClient` hook:
 *
 *   import { useApiClient } from "@/lib/api/client";
 *
 *   function MyComponent() {
 *     const api = useApiClient();
 *     // api automatically attaches Authorization: Bearer <clerk_token>
 *   }
 *
 * This unauthenticated instance is intentionally kept only for public
 * endpoints (e.g., health checks) that do not require authentication.
 */
import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});
