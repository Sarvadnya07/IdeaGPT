"use client";

import { useAuth } from "@clerk/nextjs";
import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { useMemo } from "react";
import { toast } from "sonner";

import { ApiErrorPayload, normalizeApiError } from "./errors";
import { readDevTestToken } from "./dev-token";

export type { ApiErrorPayload };

export function useApiClient() {
  const { getToken } = useAuth();

  const client = useMemo(() => {
    const instance = axios.create({
      baseURL:
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
      timeout: 45000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    instance.interceptors.request.use(
      async (config: InternalAxiosRequestConfig) => {
        try {
          let token = await getToken();
          if (!token) {
            // Development/E2E only — hard-disabled in production builds.
            token = readDevTestToken();
          }
          if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        } catch (error) {
          console.error("Failed to fetch Clerk token", error);
        }
        return config;
      },
      (error) => Promise.reject(error),
    );

    instance.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiErrorPayload>) => {
        toast.error(normalizeApiError(error).message);
        return Promise.reject(error);
      },
    );

    return instance;
  }, [getToken]);

  return client;
}
