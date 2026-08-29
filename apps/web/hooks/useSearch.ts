import { useQuery } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";
import { useState, useCallback, useRef, useEffect } from "react";

export interface SearchResult {
  type: "idea" | "evaluation" | "project";
  id: string;
  title: string;
  description: string;
  project_title?: string;
  url: string;
}

export function useSearch() {
  const api = useApiClient();
  const [query, setQueryRaw] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const setQuery = useCallback((q: string) => {
    setQueryRaw(q);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setDebouncedQuery(q), 300);
  }, []);

  useEffect(
    () => () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    },
    [],
  );

  const search = useQuery<{ results: SearchResult[]; count: number }>({
    queryKey: ["search", debouncedQuery],
    queryFn: async () => {
      if (!debouncedQuery || debouncedQuery.length < 2)
        return { results: [], count: 0 };
      const res = await api.get(
        `/search?q=${encodeURIComponent(debouncedQuery)}`,
      );
      return res.data;
    },
    enabled: debouncedQuery.length >= 2,
    staleTime: 30 * 1000,
  });

  return {
    query,
    setQuery,
    results: search.data?.results || [],
    count: search.data?.count || 0,
    isLoading: search.isLoading,
  };
}
