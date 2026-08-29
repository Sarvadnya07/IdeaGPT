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
      baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
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
      (error) => Promise.reject(error)
    );

    instance.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiErrorResponse>) => {
        const errorData = error.response?.data;
        const statusCode = error.response?.status;
        
        // Standardize Error Notifications
        if (statusCode === 401 || statusCode === 403) {
          toast.error("Session expired or unauthorized. Please log in again.");
        } else if (statusCode === 404) {
          toast.error("Resource not found.");
        } else if (statusCode && statusCode >= 500) {
          toast.error("Internal Server Error. Our team has been notified.");
        } else if (errorData?.error) {
          toast.error(errorData.error);
        } else {
          toast.error("An unexpected network error occurred.");
        }

        return Promise.reject(error);
      }
    );

    return instance;
  }, [getToken]);

  return client;
}
