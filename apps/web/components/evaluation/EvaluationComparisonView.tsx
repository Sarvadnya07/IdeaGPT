"use client";

import React from "react";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  HelpCircle,
  Clock,
  Cpu,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Layers,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  Info,
  Calendar,
} from "lucide-react";
import {
  EvaluationVersionComparisonResponse,
  DimensionDelta,
  ListDelta,
  SectionDelta,
} from "@/hooks/useEvaluationComparison";

interface EvaluationRunOption {
  id: string;
  status: string;
  created_at: string;
  score?: number | null;
  provider?: string | null;
  model?: string | null;
  evaluation_type?: string | null;
}

interface EvaluationComparisonViewProps {
  runs: EvaluationRunOption[];
  selectedA: string | null;
  selectedB: string | null;
  onSelectA: (id: string) => void;
  onSelectB: (id: string) => void;
  comparison: EvaluationVersionComparisonResponse | null | undefined;
  isLoading: boolean;
  isError: boolean;
  error?: Error | null;
}

const STATUS_BADGES: Record<
  string,
  { label: string; textClass: string; bgClass: string; icon: React.ComponentType<any> }
> = {
  improved: {
    label: "Improved",
    textClass: "text-emerald-400",
    bgClass: "bg-emerald-500/10 border-emerald-500/30",
    icon: TrendingUp,
  },
  declined: {
    label: "Declined",
    textClass: "text-rose-400",
    bgClass: "bg-rose-500/10 border-rose-500/30",
    icon: TrendingDown,
  },
  unchanged: {
    label: "Unchanged",
    textClass: "text-zinc-400",
    bgClass: "bg-zinc-800/60 border-zinc-700/60",
    icon: Minus,
  },
  unavailable: {
    label: "Unavailable",
    textClass: "text-zinc-500",
    bgClass: "bg-zinc-900 border-zinc-800",
    icon: HelpCircle,
  },
};

export function EvaluationComparisonView({
  runs,
  selectedA,
  selectedB,
  onSelectA,
  onSelectB,
  comparison,
  isLoading,
  isError,
  error,
}: EvaluationComparisonViewProps) {
  const completedRuns = runs.filter((r) => r.status === "COMPLETED");

  const runA = runs.find((r) => r.id === selectedA);
  const runB = runs.find((r) => r.id === selectedB);

  return (
    <div className="space-y-8" data-testid="evaluation-version-comparison-view">
      {/* 1. Version Selectors Bar */}
      <div className="bg-[#0e0e12] border border-zinc-800/80 rounded-2xl p-6 shadow-xl space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-800/60 pb-5">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              Select Evaluation Runs to Compare
            </h2>
            <p className="text-xs text-zinc-400 mt-1">
              Choose an earlier baseline run (Version A) and a subsequent run (Version B) to evaluate progression.
            </p>
          </div>
          {comparison && (
            <div className="text-right">
              <span className="text-[10px] uppercase tracking-wider font-semibold text-zinc-500 block">
                Analysis Engine
              </span>
              <span className="text-xs font-mono text-indigo-300">
                100% Deterministic Arithmetic
              </span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
          {/* Selector A */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
              <span className="w-5 h-5 rounded-full bg-zinc-800 text-zinc-300 inline-flex items-center justify-center text-[11px] font-bold">
                A
              </span>
              Baseline Run (Version A)
            </label>
            <select
              data-testid="selector-evaluation-a"
              value={selectedA || ""}
              onChange={(e) => onSelectA(e.target.value)}
              className="w-full px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-sm text-zinc-200 focus:outline-none focus:border-indigo-500 transition-colors"
            >
              <option value="" disabled>
                Select baseline version...
              </option>
              {completedRuns.map((r, idx) => {
                const dateStr = new Date(r.created_at).toLocaleString([], {
                  month: "short",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                });
                return (
                  <option key={`a-${r.id}`} value={r.id} disabled={r.id === selectedB}>
                    {dateStr} — Score: {r.score ?? "N/A"} ({r.provider || "engine"} / {r.model || "v1"})
                    {r.id === selectedB ? " (Selected as Version B)" : ""}
                  </option>
                );
              })}
            </select>
            {runA && (
              <div className="flex items-center gap-2 text-[11px] text-zinc-400 pt-1">
                <Calendar className="w-3 h-3 text-zinc-500" />
                <span>{new Date(runA.created_at).toLocaleString()}</span>
                <span className="text-zinc-600">•</span>
                <span className="text-zinc-300 font-semibold">
                  Score: {runA.score ?? "N/A"}
                </span>
              </div>
            )}
          </div>

          {/* Selector B */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
              <span className="w-5 h-5 rounded-full bg-indigo-900/60 text-indigo-300 border border-indigo-500/40 inline-flex items-center justify-center text-[11px] font-bold">
                B
              </span>
              Comparison Run (Version B)
            </label>
            <select
              data-testid="selector-evaluation-b"
              value={selectedB || ""}
              onChange={(e) => onSelectB(e.target.value)}
              className="w-full px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-sm text-zinc-200 focus:outline-none focus:border-indigo-500 transition-colors"
            >
              <option value="" disabled>
                Select comparison version...
              </option>
              {completedRuns.map((r) => {
                const dateStr = new Date(r.created_at).toLocaleString([], {
                  month: "short",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                });
                return (
                  <option key={`b-${r.id}`} value={r.id} disabled={r.id === selectedA}>
                    {dateStr} — Score: {r.score ?? "N/A"} ({r.provider || "engine"} / {r.model || "v1"})
                    {r.id === selectedA ? " (Selected as Version A)" : ""}
                  </option>
                );
              })}
            </select>
            {runB && (
              <div className="flex items-center gap-2 text-[11px] text-zinc-400 pt-1">
                <Calendar className="w-3 h-3 text-zinc-500" />
                <span>{new Date(runB.created_at).toLocaleString()}</span>
                <span className="text-zinc-600">•</span>
                <span className="text-zinc-300 font-semibold">
                  Score: {runB.score ?? "N/A"}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 2. Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-24 bg-[#0b0b0d] border border-zinc-800/60 rounded-2xl space-y-4">
          <Zap className="w-8 h-8 text-indigo-400 animate-bounce" />
          <p className="text-sm font-semibold text-zinc-300">
            Calculating deterministic version comparison...
          </p>
          <span className="text-xs text-zinc-500">
            Diffing overall score, dimensional progression, SWOT vectors, and sections
          </span>
        </div>
      )}

      {/* 3. Error State */}
      {isError && (
        <div className="bg-rose-950/20 border border-rose-800/50 rounded-2xl p-6 text-center space-y-3">
          <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto" />
          <h3 className="text-sm font-bold text-rose-200">Comparison Unavailable</h3>
          <p className="text-xs text-rose-300/80 max-w-md mx-auto">
            {error?.message || "Failed to load version comparison. Please verify both runs belong to this idea."}
          </p>
        </div>
      )}

      {/* 4. Empty State */}
      {!isLoading && !isError && (!selectedA || !selectedB || selectedA === selectedB) && (
        <div className="text-center py-20 bg-[#0b0b0d] border border-dashed border-zinc-800 rounded-2xl p-8 space-y-3">
          <Layers className="w-10 h-10 text-zinc-600 mx-auto" />
          <h3 className="text-base font-bold text-white">Select Two Evaluation Runs</h3>
          <p className="text-xs text-zinc-400 max-w-sm mx-auto">
            Select a distinct baseline Version A and comparison Version B from the dropdowns above to view side-by-side progression metrics.
          </p>
        </div>
      )}

      {/* 5. Main Comparison Presentation */}
      {!isLoading && !isError && comparison && (
        <div className="space-y-8" data-testid="comparison-content">
          {/* Executive Summary & Overall Score Delta */}
          <div className="bg-gradient-to-br from-[#0e0e14] via-[#0b0b0e] to-zinc-950 border border-zinc-800/80 rounded-2xl p-6 md:p-8 shadow-2xl space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="space-y-2">
                <span className="text-[10px] font-extrabold uppercase tracking-widest text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-1 rounded">
                  Executive Delta Summary
                </span>
                <h3 className="text-xl font-black text-white tracking-tight">
                  {comparison.summary}
                </h3>
              </div>

              {/* Score Delta Display Card */}
              <div
                className={`px-6 py-4 rounded-2xl border flex items-center gap-5 shadow-lg shrink-0 ${
                  STATUS_BADGES[comparison.overall_score.status]?.bgClass || "bg-zinc-900 border-zinc-800"
                }`}
              >
                <div className="text-center">
                  <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">
                    Version A
                  </span>
                  <span className="text-2xl font-black text-zinc-300">
                    {comparison.overall_score.value_a ?? "N/A"}
                  </span>
                </div>

                <ArrowRight className="w-4 h-4 text-zinc-600" />

                <div className="text-center">
                  <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">
                    Version B
                  </span>
                  <span className="text-2xl font-black text-white">
                    {comparison.overall_score.value_b ?? "N/A"}
                  </span>
                </div>

                <div className="border-l border-zinc-700/50 pl-5 text-right">
                  <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">
                    Overall Delta
                  </span>
                  <div className="flex items-center gap-1 justify-end mt-0.5">
                    <span
                      data-testid="overall-delta-value"
                      className={`text-2xl font-black tracking-tight ${
                        STATUS_BADGES[comparison.overall_score.status]?.textClass || "text-zinc-200"
                      }`}
                    >
                      {comparison.overall_score.formatted_delta ?? "N/A"}
                    </span>
                  </div>
                  <span
                    data-testid="overall-delta-badge"
                    className={`inline-block text-[10px] font-extrabold uppercase tracking-widest mt-1 ${
                      STATUS_BADGES[comparison.overall_score.status]?.textClass || "text-zinc-400"
                    }`}
                  >
                    [{STATUS_BADGES[comparison.overall_score.status]?.label}]
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Dimension-by-Dimension Progression */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-indigo-400" />
                  Dimensional Score Progression
                </h4>
                <p className="text-xs text-zinc-500">
                  Calculated against established criteria with semantic direction awareness (e.g. Lower Complexity is Improved).
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {comparison.dimensions.map((dim: DimensionDelta) => {
                const badge = STATUS_BADGES[dim.status] || STATUS_BADGES.unavailable;
                const StatusIcon = badge.icon;
                return (
                  <div
                    key={dim.key}
                    data-testid={`dimension-card-${dim.key}`}
                    className="bg-[#0c0c10] border border-zinc-800/70 rounded-xl p-4 shadow-sm space-y-3 transition-all hover:border-zinc-700"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="text-xs font-bold text-zinc-200 block">
                          {dim.label}
                        </span>
                        <span className="text-[10px] text-zinc-500 capitalize">
                          {dim.direction === "lower_is_better" ? "Lower is better" : "Higher is better"}
                        </span>
                      </div>
                      <span
                        className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${badge.textClass} ${badge.bgClass}`}
                      >
                        <StatusIcon className="w-3 h-3" />
                        {badge.label}
                      </span>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-zinc-900 text-xs">
                      <div className="text-zinc-400">
                        <span className="text-[10px] text-zinc-500 block">Run A</span>
                        <span className="font-semibold text-zinc-300">
                          {dim.value_a !== null ? dim.value_a.toFixed(1) : "Unavailable"}
                        </span>
                      </div>
                      <ArrowRight className="w-3.5 h-3.5 text-zinc-600" />
                      <div className="text-zinc-400 text-right">
                        <span className="text-[10px] text-zinc-500 block">Run B</span>
                        <span className="font-semibold text-white">
                          {dim.value_b !== null ? dim.value_b.toFixed(1) : "Unavailable"}
                        </span>
                      </div>
                      <div className="border-l border-zinc-800 pl-3 text-right">
                        <span className="text-[10px] text-zinc-500 block">Delta</span>
                        <span className={`font-mono font-bold ${badge.textClass}`}>
                          {dim.formatted_delta ?? "N/A"}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* SWOT Evolution Breakdown */}
          <div className="space-y-4">
            <div>
              <h4 className="text-base font-bold text-white flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                SWOT & Recommendations Evolution
              </h4>
              <p className="text-xs text-zinc-500">
                Deterministic text analysis highlighting newly emerged and resolved factors.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Strengths Evolution */}
              <div className="bg-[#0b0b0e] border border-zinc-800/80 rounded-xl p-5 space-y-3">
                <h5 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center justify-between">
                  <span>Strengths Evolution</span>
                  <span className="text-[10px] font-normal text-zinc-500">
                    +{comparison.swot.strengths?.added?.length || 0} / -{comparison.swot.strengths?.removed?.length || 0}
                  </span>
                </h5>
                <div className="space-y-2 text-xs">
                  {comparison.swot.strengths?.added?.map((s, i) => (
                    <div key={`sa-${i}`} className="flex items-start gap-2 text-emerald-300">
                      <span className="text-[10px] font-bold bg-emerald-500/20 px-1.5 py-0.2 rounded shrink-0">
                        NEW
                      </span>
                      <span>{s}</span>
                    </div>
                  ))}
                  {comparison.swot.strengths?.removed?.map((s, i) => (
                    <div key={`sr-${i}`} className="flex items-start gap-2 text-zinc-500 line-through">
                      <span className="text-[10px] font-bold bg-zinc-800 px-1.5 py-0.2 rounded shrink-0 text-zinc-400">
                        REMOVED
                      </span>
                      <span>{s}</span>
                    </div>
                  ))}
                  {comparison.swot.strengths?.retained?.map((s, i) => (
                    <div key={`sk-${i}`} className="flex items-start gap-2 text-zinc-400">
                      <span className="text-zinc-600">•</span>
                      <span>{s}</span>
                    </div>
                  ))}
                  {(!comparison.swot.strengths ||
                    (comparison.swot.strengths.added.length === 0 &&
                      comparison.swot.strengths.removed.length === 0 &&
                      comparison.swot.strengths.retained.length === 0)) && (
                    <p className="text-xs text-zinc-600 italic">No structured strengths recorded in either run.</p>
                  )}
                </div>
              </div>

              {/* Weaknesses Evolution */}
              <div className="bg-[#0b0b0e] border border-zinc-800/80 rounded-xl p-5 space-y-3">
                <h5 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center justify-between">
                  <span>Weaknesses Evolution</span>
                  <span className="text-[10px] font-normal text-zinc-500">
                    +{comparison.swot.weaknesses?.added?.length || 0} / -{comparison.swot.weaknesses?.removed?.length || 0}
                  </span>
                </h5>
                <div className="space-y-2 text-xs">
                  {comparison.swot.weaknesses?.removed?.map((w, i) => (
                    <div key={`wr-${i}`} className="flex items-start gap-2 text-emerald-400">
                      <span className="text-[10px] font-bold bg-emerald-500/20 px-1.5 py-0.2 rounded shrink-0">
                        RESOLVED
                      </span>
                      <span>{w}</span>
                    </div>
                  ))}
                  {comparison.swot.weaknesses?.added?.map((w, i) => (
                    <div key={`wa-${i}`} className="flex items-start gap-2 text-rose-300">
                      <span className="text-[10px] font-bold bg-rose-500/20 px-1.5 py-0.2 rounded shrink-0">
                        NEW RISK
                      </span>
                      <span>{w}</span>
                    </div>
                  ))}
                  {comparison.swot.weaknesses?.retained?.map((w, i) => (
                    <div key={`wk-${i}`} className="flex items-start gap-2 text-zinc-400">
                      <span className="text-zinc-600">•</span>
                      <span>{w}</span>
                    </div>
                  ))}
                  {(!comparison.swot.weaknesses ||
                    (comparison.swot.weaknesses.added.length === 0 &&
                      comparison.swot.weaknesses.removed.length === 0 &&
                      comparison.swot.weaknesses.retained.length === 0)) && (
                    <p className="text-xs text-zinc-600 italic">No structured weaknesses recorded in either run.</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Structured Sections Comparison */}
          {comparison.sections && comparison.sections.length > 0 && (
            <div className="space-y-4">
              <div>
                <h4 className="text-base font-bold text-white flex items-center gap-2">
                  <Info className="w-4 h-4 text-indigo-400" />
                  Structured Sections Progression
                </h4>
                <p className="text-xs text-zinc-500">
                  Presence and structural diffing of specialized report segments.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {comparison.sections.map((sec: SectionDelta) => (
                  <div
                    key={sec.section_key}
                    className="bg-[#0b0b0e] border border-zinc-800/80 rounded-xl p-4 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-zinc-200">{sec.label}</span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                          sec.status === "added"
                            ? "text-emerald-400 bg-emerald-500/10 border border-emerald-500/20"
                            : sec.status === "removed"
                            ? "text-rose-400 bg-rose-500/10 border border-rose-500/20"
                            : sec.status === "changed"
                            ? "text-indigo-300 bg-indigo-500/10 border border-indigo-500/20"
                            : sec.status === "unchanged"
                            ? "text-zinc-400 bg-zinc-800 border border-zinc-700"
                            : "text-zinc-600 bg-zinc-900 border border-zinc-800"
                        }`}
                      >
                        [{sec.status.toUpperCase()}]
                      </span>
                    </div>
                    <p className="text-xs text-zinc-400">
                      {sec.diff_summary || "No change information available."}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Execution Provenance & Timing Comparison */}
          <div className="bg-[#0b0b0e] border border-zinc-800/80 rounded-2xl p-6 space-y-4">
            <h4 className="text-xs font-extrabold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-zinc-500" />
              Execution Provenance (Read-Only Metadata)
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
              <div>
                <span className="text-[10px] font-bold uppercase text-zinc-500 block mb-1">
                  Provider & Model
                </span>
                <span className="text-zinc-300 font-mono">
                  {comparison.provenance_comparison.provider_transition}
                </span>
                <span className="text-zinc-500 block mt-0.5 font-mono text-[11px]">
                  {comparison.provenance_comparison.model_transition}
                </span>
              </div>

              <div>
                <span className="text-[10px] font-bold uppercase text-zinc-500 block mb-1">
                  Duration Delta
                </span>
                <span className="text-zinc-300">
                  {comparison.provenance_comparison.duration_ms_delta !== null
                    ? `${comparison.provenance_comparison.duration_ms_delta > 0 ? "+" : ""}${
                        comparison.provenance_comparison.duration_ms_delta
                      }ms`
                    : "N/A"}
                </span>
                <span className="text-zinc-500 block mt-0.5 text-[11px]">
                  {comparison.evaluation_a.duration_ms ?? "N/A"}ms →{" "}
                  {comparison.evaluation_b.duration_ms ?? "N/A"}ms
                </span>
              </div>

              <div>
                <span className="text-[10px] font-bold uppercase text-zinc-500 block mb-1">
                  Token Usage Delta
                </span>
                <span className="text-zinc-300">
                  {comparison.provenance_comparison.token_usage_delta !== null
                    ? `${comparison.provenance_comparison.token_usage_delta > 0 ? "+" : ""}${
                        comparison.provenance_comparison.token_usage_delta
                      } tokens`
                    : "N/A"}
                </span>
                <span className="text-zinc-500 block mt-0.5 text-[11px]">
                  {comparison.evaluation_a.token_usage ?? "N/A"} →{" "}
                  {comparison.evaluation_b.token_usage ?? "N/A"}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
