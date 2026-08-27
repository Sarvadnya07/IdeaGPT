"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useProjects } from "../../../hooks/useProjects";
import { useIdeaSubmission } from "../../../hooks/useIdeaSubmission";
import { useApiClient } from "@/lib/api/client";
import { toast } from "sonner";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Compass,
  Zap,
  Shield,
  Tag,
  Share2,
  Loader2,
  RefreshCw,
  Target,
  BarChart3,
  Layers,
  Sparkles,
  ArrowRight,
  Flame,
  Scale,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Folder,
  Plus,
} from "lucide-react";

import { DecisionGateBadge } from "@/components/strategy/DecisionGateBadge";
import { ProvenanceBadge } from "@/components/strategy/ProvenanceBadge";
import { AssumptionPriorityTable, AssumptionItemUI } from "@/components/strategy/AssumptionPriorityTable";
import { ScenarioSimulator } from "@/components/strategy/ScenarioSimulator";
import { TradeoffMatrix, TradeoffItemUI } from "@/components/strategy/TradeoffMatrix";
import { ConfidenceIndicator } from "@/components/research/ConfidenceIndicator";

interface DeepStrategyResponse {
  idea_title: string;
  decision_gate: string;
  gate_rationale: string;
  raw_attractiveness_score: number;
  normalized_risk_exposure: number;
  risk_adjusted_decision_score: number;
  scoring_formula_description: string;
  overall_confidence: string;
  key_assumptions: AssumptionItemUI[];
  decision_criteria: Array<{
    id: string;
    name: string;
    weight: number;
    raw_score: number;
    weighted_score: number;
    rationale: string;
  }>;
  tradeoffs: TradeoffItemUI[];
  scenarios: Array<{
    variant: string;
    runway_months: number;
    projected_time_to_mvp_months: number;
    feasibility_score: number;
    risk_profile: string;
    key_bottleneck: string;
    mitigation: string;
  }>;
  sensitivity_analysis: Array<{
    variable_name: string;
    baseline_value: string;
    perturbed_value: string;
    affected_dimensions: string[];
    elasticity_rating: string;
    direction: string;
    explanation: string;
  }>;
  contradictions: Array<{
    id: string;
    contradiction_type: string;
    sections_involved: string[];
    claim_a: string;
    claim_b: string;
    severity: string;
    resolution_guidance: string;
  }>;
  next_actions: Array<{
    id: string;
    action_title: string;
    action_type: string;
    rationale: string;
    target_metric: string;
    success_threshold: string;
    reversibility: string;
    target_roadmap_milestone?: string;
  }>;
}

export default function StrategyLabPage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects();
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const activeProjectId = selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const { ideasListQuery } = useIdeaSubmission(activeProjectId);
  const ideas = ideasListQuery.data || [];
  const latestIdea = ideas.length > 0 ? ideas[0] : null;

  const [activeTab, setActiveTab] = useState<"decision" | "assumptions" | "scenarios" | "tradeoffs" | "actions">("decision");

  // Strategy Analysis Mutation
  const strategyMutation = useMutation({
    mutationFn: async () => {
      if (!latestIdea) return null;
      const res = await api.post<DeepStrategyResponse>("/ai/strategy/analyze", {
        title: latestIdea.title,
        industry: latestIdea.industry || "Technology",
        problem_statement: latestIdea.problem_statement || latestIdea.title,
        solution_description: latestIdea.solution_description || latestIdea.title,
      });
      return res.data;
    },
    onSuccess: () => {
      toast.success("Strategic Decision Analysis synthesized successfully!");
    },
    onError: () => {
      toast.error("Failed to generate strategic analysis");
    },
  });

  // Link Action to Roadmap Mutation
  const linkToRoadmapMutation = useMutation({
    mutationFn: async (action: {
      action_title: string;
      rationale: string;
      target_metric: string;
      success_threshold: string;
      milestone_title?: string;
    }) => {
      if (!activeProjectId) return;
      const res = await api.post("/ai/strategy/link-to-roadmap", {
        project_id: activeProjectId,
        action_title: action.action_title,
        rationale: action.rationale,
        target_metric: action.target_metric,
        success_threshold: action.success_threshold,
        milestone_title: action.milestone_title || "Phase 1: Strategic Validation Experiments",
      });
      return res.data;
    },
    onSuccess: () => {
      toast.success("Strategic Validation Experiment added to Roadmap!");
    },
    onError: () => {
      toast.error("Failed to link experiment to roadmap");
    },
  });

  const handleAddAssumptionToRoadmap = (assumption: AssumptionItemUI) => {
    linkToRoadmapMutation.mutate({
      action_title: `Validate: ${assumption.claim.slice(0, 60)}...`,
      rationale: `High-priority assumption validation (${assumption.priority_tier}).`,
      target_metric: "Validation Experiment Completion",
      success_threshold: "Experiment proves or disproves premise with customer evidence",
      milestone_title: "Phase 1: Founder Discovery & Assumption Testing",
    });
  };

  if (projectsQuery.isLoading) {
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
          Create a project to unlock the Strategy Lab Decision Engine.
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

  const data = strategyMutation.data;

  return (
    <div className="space-y-8 max-w-6xl mx-auto p-4 md:p-8">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900/80 pb-6">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-3">
            <Compass className="w-7 h-7 text-indigo-400" />
            Strategy Lab & Decision Intelligence
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Deep reasoning, assumption testing, controlled what-if scenarios, and risk-adjusted decision modeling.
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

          <button
            onClick={() => strategyMutation.mutate()}
            disabled={strategyMutation.isPending || !latestIdea}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)]"
          >
            {strategyMutation.isPending ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> Synthesizing Strategy...
              </>
            ) : (
              <>
                <RefreshCw className="w-3.5 h-3.5" /> Execute Decision Engine
              </>
            )}
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-zinc-800/80 pb-3 overflow-x-auto">
        <button
          onClick={() => setActiveTab("decision")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "decision"
              ? "bg-indigo-600 text-white shadow-[0_0_15px_rgba(79,70,229,0.3)]"
              : "bg-zinc-900/60 text-zinc-400 hover:text-white hover:bg-zinc-800/60"
          }`}
        >
          <Target className="w-3.5 h-3.5" />
          Decision Overview
        </button>

        <button
          onClick={() => setActiveTab("assumptions")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "assumptions"
              ? "bg-amber-600 text-white shadow-[0_0_15px_rgba(217,119,6,0.3)]"
              : "bg-zinc-900/60 text-zinc-400 hover:text-white hover:bg-zinc-800/60"
          }`}
        >
          <Flame className="w-3.5 h-3.5" />
          Assumption Testing
        </button>

        <button
          onClick={() => setActiveTab("scenarios")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "scenarios"
              ? "bg-emerald-600 text-white shadow-[0_0_15px_rgba(16,185,129,0.3)]"
              : "bg-zinc-900/60 text-zinc-400 hover:text-white hover:bg-zinc-800/60"
          }`}
        >
          <Sliders className="w-3.5 h-3.5" />
          What-If Scenarios
        </button>

        <button
          onClick={() => setActiveTab("tradeoffs")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "tradeoffs"
              ? "bg-purple-600 text-white shadow-[0_0_15px_rgba(168,85,247,0.3)]"
              : "bg-zinc-900/60 text-zinc-400 hover:text-white hover:bg-zinc-800/60"
          }`}
        >
          <Scale className="w-3.5 h-3.5" />
          Trade-Offs & Reversibility
        </button>

        <button
          onClick={() => setActiveTab("actions")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "actions"
              ? "bg-cyan-600 text-white shadow-[0_0_15px_rgba(6,182,212,0.3)]"
              : "bg-zinc-900/60 text-zinc-400 hover:text-white hover:bg-zinc-800/60"
          }`}
        >
          <Zap className="w-3.5 h-3.5" />
          Actionable Roadmap Linkage
        </button>
      </div>

      {/* Main Content Area */}
      {strategyMutation.isPending ? (
        <div className="flex flex-col items-center justify-center py-20 space-y-4">
          <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
          <p className="text-xs text-zinc-400">Synthesizing deep reasoning, assumption prioritization, and scenario curves...</p>
        </div>
      ) : !data ? (
        <div className="flex flex-col items-center justify-center py-20 border border-zinc-900/60 rounded-2xl bg-[#0b0b0d] text-center p-8 space-y-4">
          <Compass className="w-12 h-12 text-zinc-700 mb-2" />
          <h3 className="text-lg font-bold text-white">No Strategy Analysis Generated Yet</h3>
          <p className="text-xs text-zinc-500 max-w-md leading-relaxed">
            Click &apos;Execute Decision Engine&apos; to run deep strategic reasoning and scenario simulations for <span className="text-white font-medium">{activeProject?.title}</span>.
          </p>
        </div>
      ) : (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* TAB 1: Decision Overview */}
          {activeTab === "decision" && (
            <div className="space-y-6">
              {/* Decision Hero Card */}
              <div className="bg-[#0b0b0d] border border-white/10 rounded-2xl p-6 space-y-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-4">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                      Decision Intelligence Engine
                    </span>
                    <h3 className="text-xl font-bold text-white flex items-center gap-3">
                      {data.idea_title}
                    </h3>
                  </div>

                  <div className="flex items-center gap-3">
                    <DecisionGateBadge gate={data.decision_gate} size="lg" />
                    <ConfidenceIndicator level={data.overall_confidence} />
                  </div>
                </div>

                <p className="text-sm text-zinc-200 leading-relaxed bg-slate-900/60 border border-white/5 p-4 rounded-xl">
                  <strong>Decision Gate Rationale:</strong> {data.gate_rationale}
                </p>

                {/* Score Breakdown Triple */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-zinc-500">Raw Attractiveness</span>
                      <ProvenanceBadge type="DETERMINISTIC_CALCULATION" />
                    </div>
                    <div className="text-2xl font-black text-white font-mono">
                      {data.raw_attractiveness_score} <span className="text-xs text-zinc-500 font-normal">/ 100</span>
                    </div>
                    <p className="text-[11px] text-zinc-400">Sum of weighted decision criteria.</p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-zinc-500">Risk Exposure (R)</span>
                      <ProvenanceBadge type="DETERMINISTIC_CALCULATION" />
                    </div>
                    <div className="text-2xl font-black text-rose-400 font-mono">
                      {data.normalized_risk_exposure} <span className="text-xs text-zinc-500 font-normal">/ 100</span>
                    </div>
                    <p className="text-[11px] text-zinc-400">Composite execution and regulatory risk factor.</p>
                  </div>

                  <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-emerald-400">Risk-Adjusted Decision Score</span>
                      <ProvenanceBadge type="DETERMINISTIC_CALCULATION" />
                    </div>
                    <div className="text-2xl font-black text-emerald-400 font-mono">
                      {data.risk_adjusted_decision_score} <span className="text-xs text-zinc-500 font-normal">/ 100</span>
                    </div>
                    <p className="text-[11px] text-emerald-300/80">
                      Score = Attractiveness × (1 - 0.5 × (R / 100)).
                    </p>
                  </div>
                </div>

                {/* Weighted Criteria Matrix */}
                <div className="space-y-3 pt-2">
                  <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">
                    Weighted Decision Criteria Breakdown
                  </h4>
                  <div className="space-y-2">
                    {data.decision_criteria.map((crit) => (
                      <div
                        key={crit.id}
                        className="p-3.5 rounded-xl bg-slate-900/40 border border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs"
                      >
                        <div className="space-y-0.5 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-white">{crit.name}</span>
                            <span className="font-mono text-[10px] text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded">
                              Weight: {(crit.weight * 100).toFixed(0)}%
                            </span>
                          </div>
                          <p className="text-zinc-400 text-[11px]">{crit.rationale}</p>
                        </div>

                        <div className="flex items-center gap-4 font-mono font-bold">
                          <span className="text-zinc-400">Raw: {crit.raw_score}</span>
                          <span className="text-emerald-400">Weighted: +{crit.weighted_score.toFixed(1)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Contradiction Warnings if any */}
                {data.contradictions && data.contradictions.length > 0 && (
                  <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 space-y-2">
                    <div className="flex items-center gap-2 text-rose-400 font-bold text-xs uppercase">
                      <AlertTriangle className="w-4 h-4" /> Cross-Section Contradictions Detected
                    </div>
                    {data.contradictions.map((c) => (
                      <div key={c.id} className="text-xs text-zinc-300 space-y-1">
                        <p><strong>Issue:</strong> {c.claim_a} vs {c.claim_b}</p>
                        <p className="text-rose-300"><strong>Guidance:</strong> {c.resolution_guidance}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: Assumptions */}
          {activeTab === "assumptions" && (
            <AssumptionPriorityTable
              assumptions={data.key_assumptions}
              onAddToRoadmap={handleAddAssumptionToRoadmap}
            />
          )}

          {/* TAB 3: Scenarios & Sensitivity */}
          {activeTab === "scenarios" && (
            <div className="space-y-8">
              <ScenarioSimulator />

              {/* Sensitivity Elasticity Table */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-bold text-white flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-emerald-400" />
                      Single-Variable Sensitivity Curves
                    </h4>
                    <p className="text-xs text-zinc-400 mt-0.5">
                      Measures which parameters materially alter venture viability when held in isolation.
                    </p>
                  </div>
                  <ProvenanceBadge type="DETERMINISTIC_CALCULATION" />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {data.sensitivity_analysis.map((s, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-2 text-xs"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white text-sm">{s.variable_name}</span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono ${
                            s.elasticity_rating === "HIGH"
                              ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                              : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          }`}
                        >
                          {s.elasticity_rating} ELASTICITY
                        </span>
                      </div>

                      <div className="flex items-center gap-3 text-[11px] text-zinc-400 font-mono">
                        <span>Baseline: <strong className="text-white">{s.baseline_value}</strong></span>
                        <span>→</span>
                        <span>Perturbed: <strong className="text-amber-400">{s.perturbed_value}</strong></span>
                      </div>

                      <p className="text-zinc-300 text-[11px] leading-relaxed">{s.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: Trade-Offs */}
          {activeTab === "tradeoffs" && (
            <TradeoffMatrix tradeoffs={data.tradeoffs} />
          )}

          {/* TAB 5: Actions & Roadmap Linkage */}
          {activeTab === "actions" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-white flex items-center gap-2">
                    <Zap className="w-4 h-4 text-cyan-400" />
                    Strategic Next Actions & Roadmap Integration
                  </h4>
                  <p className="text-xs text-zinc-400 mt-0.5">
                    Convert critical strategic validation experiments directly into active product roadmap tasks.
                  </p>
                </div>
                <ProvenanceBadge type="RECOMMENDATION" />
              </div>

              <div className="space-y-3">
                {data.next_actions.map((act) => (
                  <div
                    key={act.id}
                    className="p-5 rounded-2xl bg-[#0b0b0d] border border-white/10 space-y-3"
                  >
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-white/5 pb-3">
                      <div>
                        <span className="text-[10px] font-mono font-bold uppercase text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded">
                          {act.action_type}
                        </span>
                        <h5 className="text-sm font-bold text-white mt-1.5">{act.action_title}</h5>
                      </div>

                      <button
                        onClick={() =>
                          linkToRoadmapMutation.mutate({
                            action_title: act.action_title,
                            rationale: act.rationale,
                            target_metric: act.target_metric,
                            success_threshold: act.success_threshold,
                            milestone_title: act.target_roadmap_milestone,
                          })
                        }
                        disabled={linkToRoadmapMutation.isPending}
                        className="shrink-0 flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition shadow-[0_0_12px_rgba(79,70,229,0.3)]"
                      >
                        <Plus className="w-3.5 h-3.5" />
                        Add to Roadmap
                      </button>
                    </div>

                    <p className="text-xs text-zinc-300 leading-relaxed">{act.rationale}</p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px] pt-1">
                      <div className="p-2.5 rounded-lg bg-slate-900/60 border border-white/5">
                        <span className="text-zinc-500 font-bold uppercase text-[10px] block">Target Metric</span>
                        <span className="text-zinc-200">{act.target_metric}</span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-500/20">
                        <span className="text-emerald-400 font-bold uppercase text-[10px] block">Success Threshold</span>
                        <span className="text-emerald-200">{act.success_threshold}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
