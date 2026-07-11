import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import axios from "axios";

// Setup axios instance with dynamic token
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
});

api.interceptors.request.use(async (config) => {
  // We can inject the clerk token here, but it's easier to pass it from the hook
  return config;
});

export interface Project {
  id: number;
  user_id: number;
  title: string;
  slug: string;
  description: string;
  category: string;
  status: string;
  visibility: string;
  color: string;
  icon: string;
  is_pinned: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedProjects {
  items: Project[];
  total: number;
}

export const useProjects = (
  options: {
    limit?: number;
    offset?: number;
    search?: string;
    category?: string;
    is_archived?: boolean | null;
    is_pinned?: boolean | null;
    sort_by?: string;
  } = {}
) => {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  const getHeaders = async () => {
    const token = await getToken();
    return { Authorization: `Bearer ${token}` };
  };

  const projectsQuery = useQuery({
    queryKey: ["projects", options],
    queryFn: async () => {
      const headers = await getHeaders();
      const params = new URLSearchParams();
      if (options.limit) params.append("limit", options.limit.toString());
      if (options.offset) params.append("offset", options.offset.toString());
      if (options.search) params.append("search", options.search);
      if (options.category) params.append("category", options.category);
      if (options.is_archived !== undefined && options.is_archived !== null) 
        params.append("is_archived", options.is_archived.toString());
      if (options.is_pinned !== undefined && options.is_pinned !== null) 
        params.append("is_pinned", options.is_pinned.toString());
      if (options.sort_by) params.append("sort_by", options.sort_by);

      const res = await api.get<PaginatedProjects>(`/projects/?${params.toString()}`, { headers });
      return res.data;
    },
  });

  const createProject = useMutation({
    mutationFn: async (data: Partial<Project>) => {
      const headers = await getHeaders();
      const res = await api.post<Project>("/projects/", data, { headers });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  const updateProject = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<Project> }) => {
      const headers = await getHeaders();
      const res = await api.patch<Project>(`/projects/${id}`, data, { headers });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
  
  const togglePin = useMutation({
    mutationFn: async (id: number) => {
      const headers = await getHeaders();
      const res = await api.patch<Project>(`/projects/${id}/pin`, {}, { headers });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
  
  const toggleArchive = useMutation({
    mutationFn: async (id: number) => {
      const headers = await getHeaders();
      const res = await api.patch<Project>(`/projects/${id}/archive`, {}, { headers });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  const deleteProject = useMutation({
    mutationFn: async (id: number) => {
      const headers = await getHeaders();
      await api.delete(`/projects/${id}`, { headers });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  const duplicateProject = useMutation({
    mutationFn: async (id: number) => {
      const headers = await getHeaders();
      const res = await api.post<Project>(`/projects/${id}/duplicate`, {}, { headers });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  return {
    projectsQuery,
    createProject,
    updateProject,
    togglePin,
    toggleArchive,
    deleteProject,
    duplicateProject,
  };
};
