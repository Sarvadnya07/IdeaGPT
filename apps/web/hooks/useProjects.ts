import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

export interface Project {
  id: string;
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
  const api = useApiClient();
  const queryClient = useQueryClient();

  const projectsQuery = useQuery({
    queryKey: ["projects", options],
    queryFn: async () => {
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

      const res = await api.get<PaginatedProjects>(`/projects/?${params.toString()}`);
      return res.data;
    },
  });

  const createProject = useMutation({
    mutationFn: async (data: Partial<Project>) => {
      const res = await api.post<Project>("/projects/", data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  const updateProject = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Project> }) => {
      const res = await api.patch<Project>(`/projects/${id}`, data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
  
  const togglePin = useMutation({
    mutationFn: async (id: string) => {
      const res = await api.patch<Project>(`/projects/${id}/pin`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
  
  const toggleArchive = useMutation({
    mutationFn: async (id: string) => {
      const res = await api.patch<Project>(`/projects/${id}/archive`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  const deleteProject = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/projects/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  const duplicateProject = useMutation({
    mutationFn: async (id: string) => {
      const res = await api.post<Project>(`/projects/${id}/duplicate`);
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
