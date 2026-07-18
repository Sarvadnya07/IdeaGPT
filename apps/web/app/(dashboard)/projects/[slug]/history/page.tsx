"use client";

import React, { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useProjects } from "../../../../../hooks/useProjects";
import { useEvaluationHistory } from "../../../../../hooks/useEvaluationHistory";
import { useIdea } from "../../../../../hooks/useIdea";

import {
  ChevronLeft,
  History,
  Loader2,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Zap,
  ExternalLink,
  BarChart3,
} from "lucide-react";

const STATUS_CONFIG: Record<string, { color: string; icon: React.ComponentType<any>; label: string }> = {
  COMPLETED: { color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20", icon: CheckCircle2, label: "Completed" },
  FAILED: { color: "text-red-400 bg-red-500/10 border-red-500/20", icon: AlertTriangle, label: "Failed" },
  RUNNING: { color: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20", icon: Zap, label: "Running" },
  PENDING: { color: "text-zinc-400 bg-zinc-500/10 border-zinc-500/20", icon: Clock, label: "Pending" },
  QUEUED: { color: "text-purple-400 bg-purple-500/10 border-purple-500/20", icon: Clock, label: "Queued" },
  CANCELLED: { color: "text-zinc-600 bg-zinc-800 border-zinc-700", icon: AlertTriangle, label: "Cancelled" },
};

export default function EvaluationHistoryPage() {
  const { slug } = useParams<{ slug: string }>();
  const { projectsQuery } = useProjects();
  const projects = projectsQuery.data?.items || [];
  const currentProject = projects.find((p) => p.slug === slug);

  const { ideasQuery } = useIdea(currentProject?.id || null);
  const ideaId = ideasQuery.data?.[0]?.id || null;

  const { data: history, isLoading, refetch } = useEvaluationHistory(ideaId);


  return (
    <div className="max-w-4xl mx-auto space-y-8 py-8 px-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <Link
            href={`/projects/${slug}/analysis`}
            className="text-zinc-500 hover:text-white flex items-center gap-1 text-sm font-medium mb-3 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" /> Back to Analysis
          </Link>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
              <History className="w-5 h-5" />
            </div>
            <h1 className="text-3xl font-black text-white tracking-tight">Evaluation History</h1>
          </div>
          <p className="text-zinc-500 text-sm mt-1">
            All evaluation runs for <span className="text-zinc-300 font-semibold">{currentProject?.title || "this project"}</span>.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-zinc-300 bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 rounded-xl transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      {/* Timeline */}
      {isLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
        </div>
      ) : !history || history.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 bg-[#0b0b0d] border border-zinc-800/50 rounded-2xl">
          <History className="w-12 h-12 text-zinc-700 mb-4" />
          <h3 className="text-lg font-bold text-white mb-2">No Evaluation History</h3>
          <p className="text-zinc-500 text-sm text-center max-w-xs">
            Submit your idea for analysis to generate the first evaluation.
          </p>
          <Link
            href={`/projects/${slug}/analysis`}
            className="mt-6 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-bold rounded-xl transition-all"
          >
            Start Analysis
          </Link>
        </div>
      ) : (
        <div className="relative pl-6 border-l border-zinc-800 space-y-6 ml-3">
          {history.map((evaluation, idx) => {
            const cfg = STATUS_CONFIG[evaluation.status] || STATUS_CONFIG.PENDING;
            const StatusIcon = cfg.icon;
            const date = new Date(evaluation.created_at);
            const isLatest = idx === 0;

            return (
              <div key={evaluation.id} className="relative">
                {/* Timeline dot */}
                <span className="absolute -left-[31px] top-4 flex items-center justify-center w-[14px] h-[14px] rounded-full bg-zinc-950 border border-zinc-800">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      evaluation.status === "COMPLETED"
                        ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]"
                        : evaluation.status === "FAILED"
                        ? "bg-red-500"
                        : evaluation.status === "RUNNING"
                        ? "bg-indigo-500 animate-pulse"
                        : "bg-zinc-700"
                    }`}
                  />
                </span>

                {/* Card */}
                <div
                  className={`bg-[#0b0b0d] border rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] transition-all hover:border-zinc-700 ${
                    isLatest ? "border-indigo-500/30" : "border-zinc-900/60"
                  }`}
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        {isLatest && (
                          <span className="text-[9px] font-bold bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded uppercase tracking-widest">
                            Latest
                          </span>
                        )}
                        <span
                          className={`inline-flex items-center gap-1 text-[9px] font-bold px-2 py-0.5 rounded uppercase tracking-widest border ${cfg.color}`}
                        >
                          <StatusIcon className="w-3 h-3" />
                          {cfg.label}
                        </span>
                        {evaluation.evaluation_type && (
                          <span className="text-[9px] font-bold text-zinc-500 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded uppercase tracking-widest">
                            {evaluation.evaluation_type}
                          </span>
                        )}
                      </div>

                      <div className="flex flex-wrap gap-6 text-xs font-medium text-zinc-500">
                        <div>
                          <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest block mb-0.5">Date</span>
                          <span className="text-zinc-300">{date.toLocaleDateString()} {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                        </div>
                        {evaluation.provider && (
                          <div>
                            <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest block mb-0.5">Provider</span>
                            <span className="text-zinc-300">{evaluation.provider}</span>
                          </div>
                        )}
                        {evaluation.duration_ms && (
                          <div>
                            <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest block mb-0.5">Duration</span>
                            <span className="text-zinc-300">{evaluation.duration_ms}ms</span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      {evaluation.score !== undefined && evaluation.score !== null && (
                        <div className="w-16 h-16 rounded-full border-4 border-indigo-500/60 flex items-center justify-center bg-indigo-500/5">
                          <span className="text-lg font-black text-indigo-400">{evaluation.score}</span>
                        </div>
                      )}
                      {evaluation.status === "COMPLETED" && (
                        <Link
                          href={`/projects/${slug}/analysis?evaluationId=${evaluation.id}`}
                          className="flex items-center gap-1.5 text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors"
                        >
                          <BarChart3 className="w-4 h-4" />
                          View Results
                          <ExternalLink className="w-3 h-3" />
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
