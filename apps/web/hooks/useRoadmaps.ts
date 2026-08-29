import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

export interface Task {
  title: string;
  description?: string;
  estimated_days?: number;
  status: "pending" | "in_progress" | "completed";
}

export interface Milestone {
  title: string;
  objective: string;
  tasks: Task[];
}

export interface Roadmap {
  id: string;
  project_id: string;
  milestones: Milestone[];
  status: "draft" | "active" | "archived";
  created_at: string;
  updated_at: string;
}

export interface RoadmapCreate {
  milestones: Milestone[];
  status?: "draft" | "active" | "archived";
}

export interface RoadmapUpdate {
  milestones?: Milestone[];
  status?: "draft" | "active" | "archived";
}

export const useRoadmaps = (projectId: string | null) => {
  const api = useApiClient();
  const queryClient = useQueryClient();

  const roadmapsQuery = useQuery({
    queryKey: ["roadmaps", projectId],
    queryFn: async () => {
      if (!projectId) return [];
      const res = await api.get<Roadmap[]>(`/projects/${projectId}/roadmaps`);
      return res.data;
    },
    enabled: !!projectId,
  });

  const createRoadmap = useMutation({
    mutationFn: async (data: RoadmapCreate) => {
      if (!projectId) throw new Error("No project ID specified");
      const res = await api.post<Roadmap>(
        `/projects/${projectId}/roadmaps`,
        data,
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roadmaps", projectId] });
    },
  });

  const updateRoadmap = useMutation({
    mutationFn: async ({
      roadmapId,
      data,
    }: {
      roadmapId: string;
      data: RoadmapUpdate;
    }) => {
      const res = await api.patch<Roadmap>(`/roadmaps/${roadmapId}`, data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roadmaps", projectId] });
    },
  });

  const deleteRoadmap = useMutation({
    mutationFn: async (roadmapId: string) => {
      await api.delete(`/roadmaps/${roadmapId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roadmaps", projectId] });
    },
  });

  return {
    roadmapsQuery,
    createRoadmap,
    updateRoadmap,
    deleteRoadmap,
  };
};
