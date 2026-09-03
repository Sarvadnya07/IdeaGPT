"use client";

import { useAuth } from "@clerk/nextjs";
import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { useMemo } from "react";
import { toast } from "sonner";

export interface ApiErrorResponse {
  error: string;
  code: string;
  detail?: string;
}

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
          const token = await getToken();
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
      (error: AxiosError<ApiErrorResponse>) => {
        const errorData: any = error.response?.data;
        const statusCode = error.response?.status;

        // Standardize Error Notifications
        let userMessage: string | undefined;
        if (typeof errorData?.detail === "string") {
          userMessage = errorData.detail;
        } else if (Array.isArray(errorData?.detail)) {
          userMessage = errorData.detail
            .map((d: any) => d.msg || (typeof d === "string" ? d : JSON.stringify(d)))
            .join(", ");
        } else if (typeof errorData?.error === "string") {
          userMessage = errorData.error;
        }

        if (statusCode === 401 || statusCode === 403) {
          toast.error("Session expired or unauthorized. Please log in again.");
        } else if (statusCode === 429) {
          toast.error(userMessage || "Rate limit or quota exceeded. Please wait a moment.");
        } else if (statusCode === 404) {
          toast.error(userMessage || "Resource not found.");
        } else if (statusCode === 422) {
          toast.error(userMessage || "Validation error in submitted data.");
        } else if (statusCode && statusCode >= 500) {
          toast.error(userMessage || "Internal Server Error. Our team has been notified.");
        } else if (userMessage) {
          toast.error(userMessage);
        } else if (!error.response) {
          toast.error("Cannot connect to API server at http://localhost:8000. Please ensure the backend is running.");
        } else {
          toast.error("An unexpected network error occurred.");
        }

        return Promise.reject(error);
      },
    );

    return instance;
  }, [getToken]);

  return client;
}
