"use client";

import React, { useState } from "react";
import { useProjects } from "../../../hooks/useProjects";
import { useApiClient } from "@/lib/api/client";
import { toast } from "sonner";
import {
  DollarSign,
  TrendingUp,
  PieChart,
  ShieldAlert,
  Award,
  Loader2,
  RefreshCw,
  Target,
  FileSpreadsheet,
} from "lucide-react";

interface ValuationRange {
  pre_money_min_usd: number;
  pre_money_max_usd: number;
  target_raise_usd: number;
  dilution_pct: number;
  methodology: string;
}

interface InvestorScorecard {
  market_opportunity: number;
  team_and_execution: number;
  defensibility_moat: number;
  unit_economics: number;
  overall_investability: number;
}

interface FundingStage {
  stage: string;
  target_arr: string;
  key_milestones: string[];
  valuation_benchmark: string;
}

interface CapTableItem {
  stakeholder: string;
  initial_equity_pct: number;
  post_seed_equity_pct: number;
  post_series_a_pct: number;
}

interface RiskItem {
  risk_factor: string;
  severity: "LOW" | "MEDIUM" | "HIGH";
  mitigation_strategy: string;
}

interface InvestorLabResult {
  valuation_range: ValuationRange;
  investor_scorecard: InvestorScorecard;
  funding_stages: FundingStage[];
  cap_table_simulation: CapTableItem[];
  risk_matrix: RiskItem[];
  elevator_pitch: string;
}

export default function InvestorLabPage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects();
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const activeProjectId =
    selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const [targetRaise, setTargetRaise] = useState<string>("$1.5M Seed");
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<InvestorLabResult | null>(null);

  const handleGenerate = async () => {
    if (!activeProject) {
      toast.error("Please select a project first.");
      return;
    }
    setIsGenerating(true);
    try {
      const res = await api.post<InvestorLabResult>("/ai/labs/investor", {
        title: activeProject.title,
        category: activeProject.category || "B2B SaaS",
        market_size: "$10B+ TAM",
        target_raise: targetRaise,
      });
      setResult(res.data);
      toast.success("Institutional Investor Analysis generated successfully!");
    } catch (err: any) {
      toast.error("Failed to generate investor analysis");
    } finally {
      setIsGenerating(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="space-y-8 py-4 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-zinc-900 pb-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 uppercase tracking-widest gap-1.5">
              <DollarSign className="w-3 h-3" /> Investor & Valuation Lab
            </span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            {activeProject?.title || "Investor Assessment"}
          </h1>
          <p className="text-xs text-zinc-500 max-w-2xl leading-relaxed">
            Institutional VC valuation ranges, investability scorecards,
            dilution cap table modeling, and funding stage roadmaps.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3 shrink-0">
          <select
            value={activeProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="bg-[#0b0b0d] border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-amber-500"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title}
              </option>
            ))}
          </select>
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !activeProject}
            className="flex items-center gap-2 px-5 py-2.5 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(245,158,11,0.3)] cursor-pointer"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> Evaluating
                Pitch...
              </>
            ) : (
              <>
                <RefreshCw className="w-3.5 h-3.5" /> Generate VC Report
              </>
            )}
          </button>
        </div>
      </div>

      {result ? (
        <div className="space-y-6">
          {/* Top Elevator Pitch Card */}
          <div className="p-6 rounded-2xl bg-amber-950/20 border border-amber-900/40">
            <span className="text-[10px] font-bold uppercase tracking-widest text-amber-400 block mb-2">
              Institutional Investment Thesis
            </span>
            <p className="text-sm text-zinc-200 font-medium leading-relaxed italic">
              &ldquo;{result.elevator_pitch}&rdquo;
            </p>
          </div>

          {/* Valuation Range & Scores Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Valuation Summary */}
            <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">
                  Estimated Valuation
                </h3>
              </div>
              <div>
                <span className="text-2xl font-bold text-white block">
                  {formatCurrency(result.valuation_range.pre_money_min_usd)} -{" "}
                  {formatCurrency(result.valuation_range.pre_money_max_usd)}
                </span>
                <span className="text-xs text-zinc-500 mt-1 block">
                  Target Raise:{" "}
                  <strong className="text-zinc-300">
                    {formatCurrency(result.valuation_range.target_raise_usd)}
                  </strong>{" "}
                  (~{result.valuation_range.dilution_pct}% Dilution)
                </span>
              </div>
              <p className="text-[11px] text-zinc-500 pt-2 border-t border-zinc-900 font-mono">
                Methodology: {result.valuation_range.methodology}
              </p>
            </div>

            {/* Scorecard Metrics */}
            <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 md:col-span-2 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Award className="w-4 h-4 text-amber-400" />
                  <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">
                    VC Investability Scorecard
                  </h3>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300">
                  {result.investor_scorecard.overall_investability} / 100
                  Overall
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
                <div className="p-3 rounded-xl bg-black/40 border border-zinc-900 text-center">
                  <span className="text-lg font-bold text-white block">
                    {result.investor_scorecard.market_opportunity}
                  </span>
                  <span className="text-[10px] text-zinc-500 uppercase font-semibold">
                    Market TAM
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-black/40 border border-zinc-900 text-center">
                  <span className="text-lg font-bold text-white block">
                    {result.investor_scorecard.team_and_execution}
                  </span>
                  <span className="text-[10px] text-zinc-500 uppercase font-semibold">
                    Execution
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-black/40 border border-zinc-900 text-center">
                  <span className="text-lg font-bold text-white block">
                    {result.investor_scorecard.defensibility_moat}
                  </span>
                  <span className="text-[10px] text-zinc-500 uppercase font-semibold">
                    Defensibility
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-black/40 border border-zinc-900 text-center">
                  <span className="text-lg font-bold text-white block">
                    {result.investor_scorecard.unit_economics}
                  </span>
                  <span className="text-[10px] text-zinc-500 uppercase font-semibold">
                    Unit Econ
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Funding Stages & Cap Table Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Funding Stages */}
            <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-indigo-400" />
                <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">
                  Milestone Funding Stages
                </h3>
              </div>
              <div className="space-y-3">
                {result.funding_stages.map((stage, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-black/40 border border-zinc-900 space-y-2"
                  >
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-white">
                        {stage.stage}
                      </span>
                      <span className="font-mono text-emerald-400 text-[11px]">
                        {stage.valuation_benchmark}
                      </span>
                    </div>
                    <span className="text-[11px] text-zinc-400 block">
                      Target ARR: <strong>{stage.target_arr}</strong>
                    </span>
                    <ul className="text-[11px] text-zinc-500 space-y-1 list-disc list-inside pt-1">
                      {stage.key_milestones.map((m, mIdx) => (
                        <li key={mIdx}>{m}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            {/* Cap Table Simulation */}
            <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
              <div className="flex items-center gap-2">
                <PieChart className="w-4 h-4 text-purple-400" />
                <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">
                  Cap Table Dilution Simulation
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-zinc-900 text-zinc-500 text-[11px]">
                      <th className="pb-2">Stakeholder</th>
                      <th className="pb-2">Initial</th>
                      <th className="pb-2">Post-Seed</th>
                      <th className="pb-2">Post-Series A</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-900/60 text-zinc-300 font-mono">
                    {result.cap_table_simulation.map((c, idx) => (
                      <tr key={idx}>
                        <td className="py-2.5 font-sans font-medium text-white">
                          {c.stakeholder}
                        </td>
                        <td className="py-2.5">{c.initial_equity_pct}%</td>
                        <td className="py-2.5 text-amber-400">
                          {c.post_seed_equity_pct}%
                        </td>
                        <td className="py-2.5 text-indigo-400">
                          {c.post_series_a_pct}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Risk Matrix */}
          <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-red-400" />
              <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">
                Due Diligence Risk Matrix
              </h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {result.risk_matrix.map((r, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-black/40 border border-zinc-900 space-y-2"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-bold text-white">
                      {r.risk_factor}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        r.severity === "HIGH"
                          ? "bg-red-500/20 text-red-400"
                          : r.severity === "MEDIUM"
                            ? "bg-amber-500/20 text-amber-400"
                            : "bg-emerald-500/20 text-emerald-400"
                      }`}
                    >
                      {r.severity}
                    </span>
                  </div>
                  <p className="text-[11px] text-zinc-400 leading-relaxed">
                    {r.mitigation_strategy}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20 border border-zinc-900/60 rounded-2xl bg-[#0b0b0d] text-center p-8 space-y-4">
          <DollarSign className="w-12 h-12 text-zinc-700 mb-2" />
          <h3 className="text-lg font-bold text-white">
            No Investor Report Generated Yet
          </h3>
          <p className="text-xs text-zinc-500 max-w-md leading-relaxed">
            Click &quot;Generate VC Report&quot; to calculate institutional
            valuation ranges, dilution schedules, and due diligence risk
            assessments.
          </p>
        </div>
      )}
    </div>
  );
}
