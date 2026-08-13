import { useQuery } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

export interface AnalyticsSummary {
  total_projects: number;
  total_ideas: number;
  total_evaluations: number;
  total_reports: number;
  active_projects: number;
  draft_ideas: number;
  completed_evaluations: number;
  average_overall_score: number | null;
}

export interface ProjectMetrics {
  total: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
}

export interface IdeaMetrics {
  total: number;
  drafts: number;
  published: number;
  average_per_project: number;
}

export interface EvaluationMetrics {
  total: number;
  completed: number;
  failed: number;
  cancelled: number;
  average_score: number | null;
  score_distribution: Record<string, number>;
  dimensional_averages: Record<string, number>;
}

export interface ReportMetrics {
  total: number;
  by_type: Record<string, number>;
}

export interface TrendPoint {
  date: string;
  projects_count: number;
  ideas_count: number;
  evaluations_count: number;
}

export interface AnalyticsResponse {
  time_range: string;
  summary: AnalyticsSummary;
  projects: ProjectMetrics;
  ideas: IdeaMetrics;
  evaluations: EvaluationMetrics;
  reports: ReportMetrics;
  trends: TrendPoint[];
}

export function useAnalytics(range: string = "all", projectId?: string) {
  const api = useApiClient();

  const analyticsQuery = useQuery<AnalyticsResponse>({
    queryKey: ["analytics", range, projectId],
    queryFn: async () => {
      const params: Record<string, string> = { range };
      if (projectId) params.project_id = projectId;
      const res = await api.get<AnalyticsResponse>("/analytics", { params });
      return res.data;
    },
    staleTime: 60 * 1000, // 1 minute
  });

  return { analyticsQuery };
}
