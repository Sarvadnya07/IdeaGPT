/**
 * Framework-free API error normalisation.
 *
 * Pulled out of the Axios response interceptor so the error→message policy is
 * a pure function: it can be unit tested without React, Clerk, or a live
 * client, and the interceptor stays a thin "show a toast" shim.
 */

/** A single field-level validation failure from the backend 422 contract. */
export interface ApiValidationIssue {
  name: string;
  reason: string;
  type?: string;
}

/** The structured error body the API returns (RFC-7807-shaped). */
export interface ApiErrorPayload {
  title?: string;
  status?: number;
  error?: string;
  code?: string;
  detail?: string | Array<{ msg?: string } | string>;
  invalid_params?: ApiValidationIssue[];
}

/** A normalized, UI-ready description of a failed request. */
export interface NormalizedApiError {
  status?: number;
  /** Message suitable for display to the user. */
  message: string;
  /** True when the request never reached the server. */
  isNetworkError: boolean;
  /** Raw structured payload when present, for callers needing more detail. */
  payload?: ApiErrorPayload;
}

function extractServerMessage(detail: ApiErrorPayload["detail"]): string | undefined {
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }
  if (Array.isArray(detail)) {
    const parts = detail
      .map((entry) => {
        if (typeof entry === "string") return entry;
        if (entry && typeof entry.msg === "string") return entry.msg;
        return undefined;
      })
      .filter((part): part is string => Boolean(part && part.trim()));
    if (parts.length > 0) {
      return parts.join(", ");
    }
  }
  return undefined;
}

/**
 * Derive the user-facing message and metadata for any caught request error.
 *
 * Accepts `unknown` so it is safe to call from a catch block without a cast.
 */
export function normalizeApiError(error: unknown): NormalizedApiError {
  const axiosLike = error as {
    response?: { status?: number; data?: ApiErrorPayload };
  } | null;

  const status = axiosLike?.response?.status;
  const payload = axiosLike?.response?.data;
  const serverMessage =
    extractServerMessage(payload?.detail) ??
    (typeof payload?.error === "string" ? payload.error : undefined);

  if (status === 401 || status === 403) {
    return {
      status,
      payload,
      isNetworkError: false,
      message: "Session expired or unauthorized. Please log in again.",
    };
  }
  if (status === 429) {
    return {
      status,
      payload,
      isNetworkError: false,
      message: serverMessage ?? "Rate limit or quota exceeded. Please wait a moment.",
    };
  }
  if (status === 404) {
    return {
      status,
      payload,
      isNetworkError: false,
      message: serverMessage ?? "Resource not found.",
    };
  }
  if (status === 422) {
    return {
      status,
      payload,
      isNetworkError: false,
      message: serverMessage ?? "Validation error in submitted data.",
    };
  }
  if (typeof status === "number" && status >= 500) {
    return {
      status,
      payload,
      isNetworkError: false,
      message: serverMessage ?? "Internal Server Error. Our team has been notified.",
    };
  }
  if (axiosLike?.response) {
    return {
      status,
      payload,
      isNetworkError: false,
      message: serverMessage ?? "An unexpected network error occurred.",
    };
  }
  return {
    isNetworkError: true,
    message:
      "Cannot connect to API server at http://localhost:8000. Please ensure the backend is running.",
  };
}
