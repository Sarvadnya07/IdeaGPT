import { api } from './index';
import { AxiosResponse } from 'axios';

export interface Task {
  title: string;
  description?: string;
  estimated_days?: number;
  status: 'pending' | 'in_progress' | 'completed';
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
  status: 'draft' | 'active' | 'archived';
  created_at: string;
  updated_at: string;
}

export interface RoadmapCreate {
  milestones: Milestone[];
  status?: 'draft' | 'active' | 'archived';
}

export const roadmapsApi = {
  createRoadmap: (projectId: string, data: RoadmapCreate) =>
    api.post<Roadmap>(`/projects/${projectId}/roadmaps`, data).then((res: AxiosResponse<Roadmap>) => res.data),

  getProjectRoadmaps: (projectId: string) =>
    api.get<Roadmap[]>(`/projects/${projectId}/roadmaps`).then((res: AxiosResponse<Roadmap[]>) => res.data),

  getRoadmap: (roadmapId: string) =>
    api.get<Roadmap>(`/roadmaps/${roadmapId}`).then((res: AxiosResponse<Roadmap>) => res.data),

  updateRoadmap: (roadmapId: string, data: Partial<RoadmapCreate>) =>
    api.patch<Roadmap>(`/roadmaps/${roadmapId}`, data).then((res: AxiosResponse<Roadmap>) => res.data),

  deleteRoadmap: (roadmapId: string) =>
    api.delete(`/roadmaps/${roadmapId}`).then((res: AxiosResponse<any>) => res.data),
};
