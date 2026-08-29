"use client";

import React from "react";
import { GitCompare, ArrowRight, TrendingUp, TrendingDown, Plus, Minus } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export interface VersionDiffData {
  version_a: {
    id: string;
    created_at?: string;
    provider?: string;
    score: number;
    decision_gate: string;
  };
  version_b: {
    id: string;
    created_at?: string;
    provider?: string;
    score: number;
    decision_gate: string;
  };
  score_delta: number;
  decision_gate_changed: boolean;
  new_strengths_identified: string[];
  removed_strengths: string[];
  new_weaknesses_flagged: string[];
  resolved_weaknesses: string[];
  summary_comparison: string;
}

interface ReportVersionDiffProps {
  diffData?: VersionDiffData;
}

export const ReportVersionDiff: React.FC<ReportVersionDiffProps> = ({
  diffData = {
    version_a: {
      id: "eval-v1",
      created_at: "2026-08-20T10:00:00Z",
      provider: "groq",
      score: 72.0,
      decision_gate: "VALIDATE_FIRST"
    },
    version_b: {
      id: "eval-v2",
      created_at: "2026-08-29T14:30:00Z",
      provider: "groq",
      score: 84.0,
      decision_gate: "GO"
    },
    score_delta: 12.0,
    decision_gate_changed: true,
    new_strengths_identified: [
      "Verified B2B willingness-to-pay with LOI commitments",
      "Defensible workflow lock-in via custom API connectors"
    ],
    removed_strengths: [],
    new_weaknesses_flagged: [],
    resolved_weaknesses: [
      "Unverified customer acquisition channel"
    ],
    summary_comparison: "Version B score increased by +12.0 points (72 -> 84). Decision gate upgraded from 'VALIDATE_FIRST' to 'GO'."
  }
}) => {
  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-4 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GitCompare className="h-5 w-5 text-indigo-400" />
            <CardTitle className="text-base font-bold text-slate-100">
              Evaluation Version Comparison &amp; Audit Diff
            </CardTitle>
          </div>
          <span className="text-[10px] font-mono uppercase bg-slate-800 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
            Semantic Diffing
          </span>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Score & Gate Progression Comparison */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold text-slate-400">Baseline (Version A)</div>
            <div className="text-2xl font-black text-slate-300">{diffData.version_a.score}<span className="text-xs text-slate-500 font-normal">/100</span></div>
            <div className="text-xs font-mono text-slate-400">Gate: {diffData.version_a.decision_gate}</div>
          </div>

          <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/30 flex flex-col justify-center items-center text-center space-y-1">
            <div className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider">Score Progression</div>
            <div className="text-2xl font-black text-emerald-400 flex items-center gap-1">
              {diffData.score_delta >= 0 ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
              {diffData.score_delta >= 0 ? `+${diffData.score_delta}` : diffData.score_delta} pts
            </div>
            <div className="text-[11px] text-slate-400">{diffData.summary_comparison}</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold text-slate-400">Current (Version B)</div>
            <div className="text-2xl font-black text-indigo-300">{diffData.version_b.score}<span className="text-xs text-slate-500 font-normal">/100</span></div>
            <div className="text-xs font-mono text-emerald-400 font-bold">Gate: {diffData.version_b.decision_gate}</div>
          </div>
        </div>

        {/* Semantic Changes List */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* New Strengths */}
          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <Plus className="h-3.5 w-3.5" />
              <span>New Strengths Validated</span>
            </div>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {diffData.new_strengths_identified.map((s, idx) => (
                <li key={idx} className="flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shrink-0" />
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Resolved Weaknesses */}
          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="text-xs font-bold text-sky-400 uppercase tracking-wider flex items-center gap-1.5">
              <Minus className="h-3.5 w-3.5" />
              <span>Resolved Weaknesses / Risks</span>
            </div>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {diffData.resolved_weaknesses.map((w, idx) => (
                <li key={idx} className="flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-sky-400 shrink-0" />
                  <span>{w}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
