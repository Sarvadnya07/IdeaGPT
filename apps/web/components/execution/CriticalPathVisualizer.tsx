"use client";

import React from "react";
import { GitCommit, ArrowRight, ShieldAlert, CheckCircle2, Clock } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export interface CriticalPathData {
  total_tasks_count: number;
  estimated_total_duration_days: number;
  critical_path_duration_days: number;
  critical_path_tasks: string[];
  blocked_tasks: string[];
  parallel_workstreams: string[];
}

interface CriticalPathVisualizerProps {
  data?: CriticalPathData;
}

export const CriticalPathVisualizer: React.FC<CriticalPathVisualizerProps> = ({
  data = {
    total_tasks_count: 5,
    estimated_total_duration_days: 34,
    critical_path_duration_days: 25,
    critical_path_tasks: [
      "Customer Discovery & Problem Validation",
      "Core AI Decision Pipeline & Schema",
      "Interactive Frontend Strategy Workspace",
      "Production Deployment & Security Hardening"
    ],
    blocked_tasks: [
      "Interactive Frontend Strategy Workspace",
      "Production Deployment & Security Hardening"
    ],
    parallel_workstreams: [
      "Documentation & Investor Pitch Deck"
    ]
  }
}) => {
  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-4 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GitCommit className="h-5 w-5 text-indigo-400" />
            <CardTitle className="text-base font-bold text-slate-100">
              Critical Path &amp; Dependency Graph
            </CardTitle>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
            <Clock className="h-3.5 w-3.5 text-indigo-400" />
            <span>Critical Duration: {data.critical_path_duration_days} days</span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Critical Chain Sequence */}
        <div>
          <div className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">
            Critical Path Sequence (Longest Blocking Chain)
          </div>
          <div className="flex flex-col md:flex-row items-stretch md:items-center gap-2 overflow-x-auto pb-2">
            {data.critical_path_tasks.map((task, idx) => (
              <React.Fragment key={idx}>
                <div className="p-3 rounded-lg bg-indigo-950/30 border border-indigo-500/30 min-w-[200px] flex-1">
                  <div className="text-[10px] font-mono text-indigo-400 font-bold">STEP {idx + 1}</div>
                  <div className="text-xs font-semibold text-slate-200 mt-0.5">{task}</div>
                </div>
                {idx < data.critical_path_tasks.length - 1 && (
                  <ArrowRight className="h-4 w-4 text-indigo-400 hidden md:block shrink-0" />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Blocked & Parallel Streams Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-amber-400">
              <ShieldAlert className="h-4 w-4" />
              <span>Blocked Tasks (Awaiting Pre-requisites)</span>
            </div>
            <ul className="space-y-1.5 text-xs text-slate-400">
              {data.blocked_tasks.map((b, idx) => (
                <li key={idx} className="flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
                  <span>{b}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400">
              <CheckCircle2 className="h-4 w-4" />
              <span>Parallel Workstreams (Non-blocking)</span>
            </div>
            <ul className="space-y-1.5 text-xs text-slate-400">
              {data.parallel_workstreams.map((p, idx) => (
                <li key={idx} className="flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  <span>{p}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
