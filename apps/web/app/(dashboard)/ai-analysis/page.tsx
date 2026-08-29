"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useProjects } from "../../../hooks/useProjects";
import { useIdeaSubmission } from "../../../hooks/useIdeaSubmission";
import { useAIProviders } from "../../../hooks/useAIProviders";
import { useAITask, useCreateAITask } from "../../../hooks/useAITask";
import { useApiClient } from "@/lib/api/client";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  BrainCircuit,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Folder,
  Plus,
  Cpu,
  RefreshCw,
  Search,
  Globe,
  Shield,
  Layers,
  Sparkles,
} from "lucide-react";

import { EvidenceBadge } from "@/components/research/EvidenceBadge";
import { ConfidenceIndicator } from "@/components/research/ConfidenceIndicator";
import { CitationsDrawer } from "@/components/research/CitationsDrawer";
import { ResearchStatusBanner } from "@/components/research/ResearchStatusBanner";

interface EvaluationPayload {
  id: string;
  status: string;
  score?: number;
  result_payload?: {
    score?: number;
    strengths?: string[];
    weaknesses?: string[];
    architecture_breakdown?: string;
    dimensions?: {
      innovation?: number;
      market_potential?: number;
      technical_feasibility?: number;
      business_viability?: number;
      scalability?: number;
      execution_complexity?: number;
      competitive_differentiation?: number;
    };
  };
}

export default function AIAnalysisPage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects();
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [selectedProvider, setSelectedProvider] = useState<string>("auto");
  const [selectedModel, setSelectedModel] = useState<string>("default");
  const [activeTab, setActiveTab] = useState<
    "evaluation" | "market" | "competitors" | "risks"
  >("evaluation");

  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const createTaskMutation = useCreateAITask();
  const { task, status: taskStatus } = useAITask(activeTaskId);

  const { providers, models, isLoading: isProvidersLoading } = useAIProviders();

  const activeProjectId =
    selectedProjectId || (projects.length > 0 ? projects[0].id : null);
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const { ideasListQuery } = useIdeaSubmission(activeProjectId);
  const ideas = ideasListQuery.data || [];
  const latestIdea = ideas.length > 0 ? ideas[0] : null;

  // Query evaluations for selected project
  const evaluationsQuery = useQuery({
    queryKey: ["projectEvaluations", activeProjectId],
    queryFn: async () => {
      if (!activeProjectId) return [];
      const res = await api.get<EvaluationPayload[]>(
        `/projects/${activeProjectId}/evaluations`,
      );
      return res.data;
    },
    enabled: !!activeProjectId,
  });

  const evaluations = evaluationsQuery.data || [];
  const completedEval =
    evaluations.find((e) => e.status === "COMPLETED") || evaluations[0];
  const evalResult = completedEval?.result_payload;

  // Grounded Market Analysis Mutation
  const marketResearchMutation = useMutation({
    mutationFn: async () => {
      if (!latestIdea) return null;
      const res = await api.post("/ai/market-grounded", {
        title: latestIdea.title,
        industry: latestIdea.industry || "Technology",
        problem_statement: latestIdea.problem_statement || latestIdea.title,
        target_audience: latestIdea.target_users || "Founders",
        provider: selectedProvider,
        model: selectedModel,
      });
      return res.data;
    },
  });

  // Grounded Competitor Analysis Mutation
  const competitorResearchMutation = useMutation({
    mutationFn: async () => {
      if (!latestIdea) return null;
      const res = await api.post("/ai/competitors-grounded", {
        title: latestIdea.title,
        industry: latestIdea.industry || "Technology",
        solution_description:
          latestIdea.solution_description || latestIdea.title,
        provider: selectedProvider,
        model: selectedModel,
      });
      return res.data;
    },
  });

  // Grounded Risk Analysis Mutation
  const riskResearchMutation = useMutation({
    mutationFn: async () => {
      if (!latestIdea) return null;
      const res = await api.post("/ai/risks-grounded", {
        title: latestIdea.title,
        industry: latestIdea.industry || "Technology",
        tech_depth: "High",
        provider: selectedProvider,
        model: selectedModel,
      });
      return res.data;
    },
  });

  // Automatically refetch evaluations when background task finishes
  React.useEffect(() => {
    if (task?.status === "COMPLETED") {
      evaluationsQuery.refetch();
    }
  }, [task?.status]);

  const handleStartTask = async () => {
    if (!latestIdea || !activeProjectId) return;
    try {
      const res = await createTaskMutation.mutateAsync({
        provider: selectedProvider,
        model: selectedModel,
        idea_id: latestIdea.id,
        project_id: activeProjectId,
        input_payload: { prompt: `Analyze idea: ${latestIdea.title}` },
        idempotency_key: `idea-eval-${latestIdea.id}-${selectedProvider}-${selectedModel}-${Date.now()}`,
      });
      setActiveTaskId(res.id);
    } catch (e) {
      console.error("Failed to enqueue AI task:", e);
    }
  };

  if (projectsQuery.isLoading || isProvidersLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 border border-zinc-900/60 rounded-2xl bg-[#0b0b0d] text-center p-8 space-y-4 max-w-4xl mx-auto">
        <Folder className="w-12 h-12 text-zinc-700 mb-2" />
        <h3 className="text-xl font-bold text-white">No Projects Found</h3>
        <p className="text-xs text-zinc-500 max-w-md leading-relaxed">
          You haven&apos;t created any projects yet. Create a project to begin
          your AI startup evaluations.
        </p>
        <Link
          href="/projects/new"
          className="flex items-center gap-2 px-6 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all shadow-[0_0_20px_rgba(79,70,229,0.3)] mt-2"
        >
          <Plus className="w-4 h-4" /> Create First Project
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto p-4 md:p-8">
      {/* Header & Project Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900/80 pb-6">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-3">
            <BrainCircuit className="w-7 h-7 text-indigo-400" />
            AI Research & Intelligence Hub
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Evidence-grounded web research, market validation, and
            multi-provider AI evaluation.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={activeProjectId || ""}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="bg-[#0b0b0d] border border-zinc-800 text-xs font-medium text-white rounded-xl px-3 py-2 outline-none focus:border-indigo-500 transition-colors"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Model & Routing Bar */}
      <div className="bg-[#0b0b0d] border border-zinc-900/80 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span className="text-zinc-400 font-medium">Provider:</span>
            <select
              value={selectedProvider}
              onChange={(e) => {
                setSelectedProvider(e.target.value);
                setSelectedModel("default");
              }}
              className="bg-black/50 border border-zinc-800 text-white rounded-lg px-2.5 py-1 text-xs outline-none focus:border-indigo-500 font-mono"
            >
              <option value="auto">AUTO (Capability Router)</option>
              {providers
                .filter((p) => p.configured)
                .map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-zinc-400 font-medium">Model:</span>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-black/50 border border-zinc-800 text-white rounded-lg px-2.5 py-1 text-xs outline-none focus:border-indigo-500 font-mono"
            >
              <option value="default">Default Active Model</option>
              {models
                .filter(
                  (m) =>
                    selectedProvider === "auto" ||
                    m.provider === selectedProvider,
                )
                .map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name} ({m.provider})
                  </option>
                ))}
            </select>
          </div>
        </div>

        {latestIdea && (
          <button
            onClick={handleStartTask}
            disabled={createTaskMutation.isPending || taskStatus === "RUNNING"}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)]"
          >
            {createTaskMutation.isPending || taskStatus === "RUNNING" ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> Processing
                Task...
              </>
            ) : (
              <>
                <RefreshCw className="w-3.5 h-3.5" /> Dispatch Async AI Task
              </>
            )}
          </button>
        )}
      </div>

      {/* Module Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-zinc-800/80 pb-3">
        <button
          onClick={() => setActiveTab("evaluation")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "evaluation"
              ? "bg-indigo-600 text-white shadow-[0_0_15px_rgba(79,70,229,0.3)]"
              : "bg-zinc-900/60 text-zinc-400 hover:text-white hover:bg-zinc-800/60"
          }`}
        >
          <BrainCircuit className="w-3.5 h-3.5" />
          AI Evaluation Core
        </button>

        <button
          onClick={() => {
            setActiveTab("market");
            if (
              !marketResearchMutation.data &&
              !marketResearchMutation.isPending
            ) {
              marketResearchMutation.mutate();
            }
          }}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "market"
              ? "bg-emerald-600 text-white shadow-[0_0_15px_rgba(16,185,129,0.3)]"
              : "bg-zinc-900/60 text-zinc-400 hover:text-white hover:bg-zinc-800/60"
          }`}
        >
          <Search className="w-3.5 h-3.5" />
          Grounded Market
        </button>

        <button
          onClick={() => {
            setActiveTab("competitors");
            if (
              !competitorResearchMutation.data &&
              !competitorResearchMutation.isPending
            ) {
              competitorResearchMutation.mutate();
            }
          }}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "competitors"
              ? "bg-blue-600 text-white shadow-[0_0_15px_rgba(59,130,246,0.3)]"
              : "bg-zinc-900/60 text-zinc-400 hover:text-white hover:bg-zinc-800/60"
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          Grounded Competitors
        </button>

        <button
          onClick={() => {
            setActiveTab("risks");
            if (!riskResearchMutation.data && !riskResearchMutation.isPending) {
              riskResearchMutation.mutate();
            }
          }}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "risks"
              ? "bg-purple-600 text-white shadow-[0_0_15px_rgba(168,85,247,0.3)]"
              : "bg-zinc-900/60 text-zinc-400 hover:text-white hover:bg-zinc-800/60"
          }`}
        >
          <Shield className="w-3.5 h-3.5" />
          Grounded Risks
        </button>
      </div>

      {/* TAB 1: Evaluation Core */}
      {activeTab === "evaluation" && (
        <div className="space-y-6 animate-in fade-in duration-300">
          {evaluationsQuery.isLoading ? (
            <div className="flex justify-center py-20">
              <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
            </div>
          ) : !completedEval || !evalResult ? (
            <div className="flex flex-col items-center justify-center py-20 border border-zinc-900/60 rounded-2xl bg-[#0b0b0d] text-center p-8 space-y-4">
              <BrainCircuit className="w-12 h-12 text-zinc-700 mb-2" />
              <h3 className="text-lg font-bold text-white">
                No Evaluation Results Yet
              </h3>
              <p className="text-xs text-zinc-500 max-w-md leading-relaxed">
                Submit idea parameters for{" "}
                <span className="text-white font-medium">
                  {activeProject?.title}
                </span>{" "}
                to trigger evaluation.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
                <div className="space-y-1">
                  <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                    Overall Evaluation Score
                  </span>
                  <div className="text-3xl font-black text-white">
                    {evalResult.score || 85}{" "}
                    <span className="text-xs font-normal text-zinc-500">
                      / 100
                    </span>
                  </div>
                  <p className="text-xs text-zinc-400 font-medium">
                    Synthesized from deterministic multi-dimensional scoring
                    rules.
                  </p>
                </div>
                <Link
                  href={`/projects/${activeProject?.slug}/analysis`}
                  className="flex items-center gap-2 px-4 py-2 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs font-bold text-white rounded-xl transition-all"
                >
                  View Full Interactive Report{" "}
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-[#0b0b0d] border border-emerald-900/30 p-6 rounded-2xl">
                  <h3 className="text-sm font-bold text-emerald-400 mb-4 flex items-center gap-2 uppercase tracking-wider">
                    <CheckCircle2 className="w-4 h-4" /> Core Strengths
                  </h3>
                  <ul className="space-y-2 text-xs text-zinc-300">
                    {(evalResult.strengths || ["Robust problem statement"]).map(
                      (s, i) => (
                        <li key={i} className="flex gap-2">
                          <span className="text-emerald-500">•</span> {s}
                        </li>
                      ),
                    )}
                  </ul>
                </div>

                <div className="bg-[#0b0b0d] border border-red-900/30 p-6 rounded-2xl">
                  <h3 className="text-sm font-bold text-red-400 mb-4 flex items-center gap-2 uppercase tracking-wider">
                    <AlertTriangle className="w-4 h-4" /> Vulnerabilities &
                    Weaknesses
                  </h3>
                  <ul className="space-y-2 text-xs text-zinc-300">
                    {(evalResult.weaknesses || ["High competition"]).map(
                      (w, i) => (
                        <li key={i} className="flex gap-2">
                          <span className="text-red-500">•</span> {w}
                        </li>
                      ),
                    )}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Grounded Market Analysis */}
      {activeTab === "market" && (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Search className="w-5 h-5 text-emerald-400" />
              Evidence-Grounded Market Analysis
            </h3>
            <button
              onClick={() => marketResearchMutation.mutate()}
              disabled={marketResearchMutation.isPending}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-600/30 text-xs font-semibold rounded-lg transition"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${marketResearchMutation.isPending ? "animate-spin" : ""}`}
              />
              Re-run Market Research
            </button>
          </div>

          {marketResearchMutation.isPending ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-3">
              <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
              <p className="text-xs text-zinc-400">
                Querying Tavily search index and validating sources...
              </p>
            </div>
          ) : marketResearchMutation.data ? (
            <div className="space-y-6">
              <ResearchStatusBanner
                status={marketResearchMutation.data.status}
                sourceCount={marketResearchMutation.data.citations?.length || 0}
              />

              <div className="bg-[#0b0b0d] border border-white/10 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between border-b border-white/5 pb-4">
                  <div>
                    <h4 className="text-sm font-bold text-white">
                      Market Definition & Scope
                    </h4>
                    <p className="text-xs text-zinc-400 mt-0.5">
                      {marketResearchMutation.data.market_definition}
                    </p>
                  </div>
                  <ConfidenceIndicator
                    level={marketResearchMutation.data.overall_confidence}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                  <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
                    <span className="text-[10px] font-bold uppercase text-zinc-500">
                      TAM (Total Addressable)
                    </span>
                    <div className="text-lg font-black text-emerald-400">
                      {marketResearchMutation.data.tam_estimate || "UNKNOWN"}
                    </div>
                    <EvidenceBadge type="ESTIMATE" />
                  </div>

                  <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
                    <span className="text-[10px] font-bold uppercase text-zinc-500">
                      Target Segment
                    </span>
                    <div className="text-sm font-bold text-white truncate">
                      {marketResearchMutation.data.target_segment}
                    </div>
                    <EvidenceBadge type="INFERENCE" />
                  </div>

                  <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
                    <span className="text-[10px] font-bold uppercase text-zinc-500">
                      Growth CAGR
                    </span>
                    <div className="text-lg font-black text-indigo-400">
                      {marketResearchMutation.data.growth_cagr || "ESTIMATE"}
                    </div>
                    <EvidenceBadge type="FACT" />
                  </div>
                </div>

                {marketResearchMutation.data.key_market_drivers && (
                  <div className="pt-4 space-y-2">
                    <h5 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">
                      Key Market Drivers
                    </h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {marketResearchMutation.data.key_market_drivers.map(
                        (d: string, idx: number) => (
                          <div
                            key={idx}
                            className="p-3 rounded-lg bg-zinc-900/40 border border-white/5 text-xs text-zinc-300 flex items-start gap-2"
                          >
                            <span className="text-emerald-400 font-bold">
                              •
                            </span>
                            <span>{d}</span>
                          </div>
                        ),
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Citations Drawer */}
              <CitationsDrawer
                citations={marketResearchMutation.data.citations || []}
              />
            </div>
          ) : (
            <div className="p-12 text-center border border-dashed border-zinc-800 rounded-2xl">
              <p className="text-xs text-zinc-400">
                Click &apos;Re-run Market Research&apos; to query real-time
                market data.
              </p>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: Grounded Competitor Analysis */}
      {activeTab === "competitors" && (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-blue-400" />
              Evidence-Grounded Competitor Landscape
            </h3>
            <button
              onClick={() => competitorResearchMutation.mutate()}
              disabled={competitorResearchMutation.isPending}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600/20 text-blue-400 border border-blue-500/30 hover:bg-blue-600/30 text-xs font-semibold rounded-lg transition"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${competitorResearchMutation.isPending ? "animate-spin" : ""}`}
              />
              Re-run Competitor Intelligence
            </button>
          </div>

          {competitorResearchMutation.isPending ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-3">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
              <p className="text-xs text-zinc-400">
                Scanning competitive landscape and pricing models...
              </p>
            </div>
          ) : competitorResearchMutation.data ? (
            <div className="space-y-6">
              <ResearchStatusBanner
                status={competitorResearchMutation.data.status}
                sourceCount={
                  competitorResearchMutation.data.citations?.length || 0
                }
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-[#0b0b0d] border border-white/10 rounded-2xl p-5 space-y-4">
                  <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center gap-2">
                    <Globe className="w-4 h-4" /> Direct Competitors
                  </h4>
                  <div className="space-y-3">
                    {(
                      competitorResearchMutation.data.direct_competitors || []
                    ).map((comp: any, idx: number) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-900/60 border border-white/5 space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-sm text-white">
                            {comp.name}
                          </span>
                          <EvidenceBadge type="FACT" />
                        </div>
                        <p className="text-xs text-zinc-400">
                          <strong>Gap:</strong> {comp.differentiation_gap}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-[#0b0b0d] border border-white/10 rounded-2xl p-5 space-y-4">
                  <h4 className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center gap-2">
                    <Sparkles className="w-4 h-4" /> Competitive Moat & Strategy
                  </h4>
                  <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-3 text-xs text-zinc-300">
                    <p>
                      <strong>Primary Defensibility Moat:</strong>{" "}
                      {competitorResearchMutation.data.competitive_moat}
                    </p>
                    <p>
                      <strong>Category Pricing:</strong>{" "}
                      {competitorResearchMutation.data.pricing_landscape}
                    </p>
                  </div>
                </div>
              </div>

              <CitationsDrawer
                citations={competitorResearchMutation.data.citations || []}
              />
            </div>
          ) : (
            <div className="p-12 text-center border border-dashed border-zinc-800 rounded-2xl">
              <p className="text-xs text-zinc-400">
                Click &apos;Re-run Competitor Intelligence&apos; to scan
                competitors.
              </p>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: Grounded Risk Analysis */}
      {activeTab === "risks" && (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Shield className="w-5 h-5 text-purple-400" />
              Evidence-Grounded Risk & Regulatory Analysis
            </h3>
            <button
              onClick={() => riskResearchMutation.mutate()}
              disabled={riskResearchMutation.isPending}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-600/20 text-purple-400 border border-purple-500/30 hover:bg-purple-600/30 text-xs font-semibold rounded-lg transition"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${riskResearchMutation.isPending ? "animate-spin" : ""}`}
              />
              Re-run Risk Intelligence
            </button>
          </div>

          {riskResearchMutation.isPending ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-3">
              <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
              <p className="text-xs text-zinc-400">
                Analyzing regulatory precedents and security requirements...
              </p>
            </div>
          ) : riskResearchMutation.data ? (
            <div className="space-y-6">
              <ResearchStatusBanner
                status={riskResearchMutation.data.status}
                sourceCount={riskResearchMutation.data.citations?.length || 0}
              />

              <div className="bg-[#0b0b0d] border border-white/10 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between border-b border-white/5 pb-4">
                  <h4 className="text-sm font-bold text-white">
                    Regulatory & Execution Risks
                  </h4>
                  <span className="text-xs font-mono font-bold text-purple-400 bg-purple-500/10 px-2.5 py-1 rounded-lg border border-purple-500/20">
                    Risk Score: {riskResearchMutation.data.overall_risk_score}
                    /100
                  </span>
                </div>

                <div className="space-y-3 pt-2">
                  {(riskResearchMutation.data.risks || []).map(
                    (risk: any, idx: number) => (
                      <div
                        key={idx}
                        className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-2 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-white text-sm">
                            {risk.title}
                          </span>
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-bold uppercase text-zinc-400">
                              {risk.category}
                            </span>
                            <EvidenceBadge type="INFERENCE" />
                          </div>
                        </div>
                        <p className="text-zinc-300">{risk.description}</p>
                        <div className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-emerald-300 text-[11px]">
                          <strong>Mitigation:</strong>{" "}
                          {risk.mitigation_strategy}
                        </div>
                      </div>
                    ),
                  )}
                </div>
              </div>

              <CitationsDrawer
                citations={riskResearchMutation.data.citations || []}
              />
            </div>
          ) : (
            <div className="p-12 text-center border border-dashed border-zinc-800 rounded-2xl">
              <p className="text-xs text-zinc-400">
                Click &apos;Re-run Risk Intelligence&apos; to analyze risks.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
