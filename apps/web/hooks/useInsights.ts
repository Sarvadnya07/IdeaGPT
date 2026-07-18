import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export interface InsightData {
  evaluation_id: string;
  executive_summary: {
    summary: string;
    score: number;
    confidence: number;
    ai_recommendation: string;
    key_opportunity: string;
    major_concern: string;
  };
  innovation: {
    score: number;
    originality: string;
    differentiation: string;
    novelty: string;
    defensibility: string;
  };
  market_analysis: {
    score: number;
    tam: string;
    sam: string;
    som: string;
    target_audience: string;
    adoption_barriers: string[];
    market_maturity: string;
  };
  competitor_analysis: {
    direct_competitors: string[];
    indirect_competitors: string[];
    existing_alternatives: string[];
    competitive_advantages: string[];
    competitive_gaps: string[];
  };
  swot: {
    strengths: string[];
    weaknesses: string[];
    opportunities: string[];
    threats: string[];
  };
  technical_feasibility: {
    score: number;
    engineering_complexity: string;
    required_technologies: string[];
    infrastructure: string;
    development_timeline: string;
    major_technical_risks: string[];
    architecture_breakdown: string;
  };
  business_model: {
    viability_score: number;
    scalability_score: number;
    revenue_model: string;
    pricing: string;
    customer_acquisition: string;
    retention: string;
    scalability_path: string;
  };
  financial_potential: {
    investment_score: number;
    year1_arr_estimate: string;
    year3_arr_estimate: string;
    funding_round_fit: string;
    burn_rate_estimate: string;
  };
  risk_analysis: {
    market_risk: { level: string; description: string; mitigation: string };
    technical_risk: { level: string; description: string; mitigation: string };
    financial_risk: { level: string; description: string; mitigation: string };
    legal_risk: { level: string; description: string; mitigation: string };
    operational_risk: { level: string; description: string; mitigation: string };
  };
  recommendations: {
    quick_wins: string[];
    medium_term: string[];
    long_term: string[];
  };
}

export function useInsights(evaluationId: string | null) {
  return useQuery<InsightData>({
    queryKey: ["insights", evaluationId],
    queryFn: async () => {
      const res = await api.get(`/evaluations/${evaluationId}/insights`);
      return res.data;
    },
    enabled: !!evaluationId,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}

export function useEvaluationScores(evaluationId: string | null) {
  return useQuery({
    queryKey: ["evaluation-scores", evaluationId],
    queryFn: async () => {
      const res = await api.get(`/evaluations/${evaluationId}/scores`);
      return res.data;
    },
    enabled: !!evaluationId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useEvaluationCharts(evaluationId: string | null) {
  return useQuery({
    queryKey: ["evaluation-charts", evaluationId],
    queryFn: async () => {
      const res = await api.get(`/evaluations/${evaluationId}/charts`);
      return res.data;
    },
    enabled: !!evaluationId,
    staleTime: 5 * 60 * 1000,
  });
}
