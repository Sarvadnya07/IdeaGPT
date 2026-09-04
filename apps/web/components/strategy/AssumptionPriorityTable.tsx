"use client";

import React from "react";
import {
  ArrowUpRight,
  Flame,
} from "lucide-react";
import { ProvenanceBadge } from "./ProvenanceBadge";

export interface AssumptionItemUI {
  id: string;
  claim: string;
  classification: string;
  impact: string;
  uncertainty: string;
  validation_ease: string;
  priority_score: number;
  priority_tier: string;
  recommended_experiment: string;
  provenance?: string;
}

interface AssumptionPriorityTableProps {
  assumptions: AssumptionItemUI[];
  onAddToRoadmap?: (assumption: AssumptionItemUI) => void;
  className?: string;
}

export const AssumptionPriorityTable: React.FC<
  AssumptionPriorityTableProps
> = ({ assumptions, onAddToRoadmap, className = "" }) => {
  if (!assumptions || assumptions.length === 0) {
    return (
      <div className="text-xs text-slate-500 italic p-4 text-center border border-zinc-800 rounded-xl">
        No unverified assumptions extracted for this idea.
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-sm font-bold text-white flex items-center gap-2">
            <Flame className="w-4 h-4 text-amber-400" />
            Prioritized Assumptions & Validation Experiments
          </h4>
          <p className="text-xs text-zinc-400 mt-0.5">
            Ranked by normalized formula: Priority = (Impact × Uncertainty) /
            Ease of Validation.
          </p>
        </div>
        <ProvenanceBadge type="DETERMINISTIC_CALCULATION" />
      </div>

      <div className="space-y-3">
        {assumptions.map((item, idx) => (
          <div
            key={item.id || idx}
            className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-3 hover:border-white/10 transition"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/5 pb-2.5">
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-mono font-black uppercase ${
                    item.priority_tier === "CRITICAL"
                      ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                      : item.priority_tier === "HIGH"
                        ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                        : "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                  }`}
                >
                  {item.priority_tier} PRIORITY (
                  {item.priority_score.toFixed(1)} / 9.0)
                </span>
                <span className="text-xs font-mono text-zinc-400">
                  #{item.classification}
                </span>
              </div>

              <div className="flex items-center gap-2 text-[11px] text-zinc-400">
                <span>
                  Impact: <strong className="text-white">{item.impact}</strong>
                </span>
                <span>•</span>
                <span>
                  Uncertainty:{" "}
                  <strong className="text-white">{item.uncertainty}</strong>
                </span>
                <span>•</span>
                <span>
                  Ease:{" "}
                  <strong className="text-white">{item.validation_ease}</strong>
                </span>
              </div>
            </div>

            <p className="text-xs text-zinc-200 leading-relaxed font-medium">
              &quot;{item.claim}&quot;
            </p>

            <div className="p-3 rounded-lg bg-indigo-950/20 border border-indigo-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div className="space-y-0.5">
                <span className="font-bold text-indigo-400 uppercase text-[10px] tracking-wider block">
                  Recommended Validation Experiment
                </span>
                <span className="text-zinc-300">
                  {item.recommended_experiment}
                </span>
              </div>

              {onAddToRoadmap && (
                <button
                  onClick={() => onAddToRoadmap(item)}
                  className="shrink-0 flex items-center gap-1 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs transition shadow-[0_0_10px_rgba(79,70,229,0.3)]"
                >
                  <ArrowUpRight className="w-3.5 h-3.5" />
                  Add to Roadmap
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
