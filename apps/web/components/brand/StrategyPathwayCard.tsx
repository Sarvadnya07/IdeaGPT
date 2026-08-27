import React from "react";
import { EvidenceBadge } from "./EvidenceBadge";
import { ArrowRight, GitFork, ShieldAlert, Sparkles, Target } from "lucide-react";

export function StrategyPathwayCard({
  title = "Authentication Architecture Validation",
  decision = "Clerk + Custom JWT Microservice",
  confidence = 94,
  className = "",
}: {
  title?: string;
  decision?: string;
  confidence?: number;
  className?: string;
}) {
  return (
    <div
      className={`rounded-2xl bg-[#101012] border border-zinc-800/80 p-5 shadow-2xl relative overflow-hidden group hover:border-zinc-700 transition-all ${className}`}
    >
      {/* Decorative gradient glow */}
      <div className="absolute top-0 right-0 w-36 h-36 bg-gradient-to-bl from-[#00C29A]/10 via-[#0284C7]/5 to-transparent rounded-full blur-2xl pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between gap-3 border-b border-zinc-800/60 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-[#00C29A]">
            <GitFork className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white tracking-tight">{title}</h4>
            <span className="text-[10px] text-zinc-400 font-mono">
              STRATEGY FLOW: IDEA → REASONING → DECISION
            </span>
          </div>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#00C29A]/10 border border-[#00C29A]/30 text-[#00C29A] text-[10px] font-bold">
          <Sparkles className="w-3 h-3" />
          <span>{confidence}% Confidence</span>
        </div>
      </div>

      {/* Decision Node Flow */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-center">
        {/* Core Decision Input */}
        <div className="bg-[#18181B] border border-zinc-800 rounded-xl p-3 flex flex-col justify-between h-full">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
              PRIMARY DECISION
            </span>
            <Target className="w-3.5 h-3.5 text-sky-400" />
          </div>
          <p className="text-xs font-bold text-zinc-100">{decision}</p>
          <div className="mt-2 pt-2 border-t border-zinc-800/80 flex items-center gap-2">
            <EvidenceBadge type="RECOMMENDATION" size="sm" />
          </div>
        </div>

        {/* Evidence Verification Points */}
        <div className="bg-[#18181B] border border-zinc-800 rounded-xl p-3 flex flex-col justify-between h-full space-y-2">
          <span className="text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
            EVIDENCE BREAKDOWN
          </span>
          <div className="flex flex-wrap gap-1.5">
            <EvidenceBadge type="FACT" label="99.9% Auth Uptime" size="sm" />
            <EvidenceBadge type="ESTIMATE" label="~2 Days Setup" size="sm" />
            <EvidenceBadge type="INFERENCE" label="Zero Token Leakage" size="sm" />
          </div>
        </div>

        {/* Risk & Action Scorecard */}
        <div className="bg-[#18181B] border border-zinc-800 rounded-xl p-3 flex flex-col justify-between h-full">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
              RISK SCORECARD
            </span>
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-zinc-400">Vendor Lock-in:</span>
              <span className="text-emerald-400 font-bold">Low Risk</span>
            </div>
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-zinc-400">Scaling Cost:</span>
              <span className="text-amber-400 font-bold">Moderate</span>
            </div>
          </div>
          <div className="mt-2 pt-2 border-t border-zinc-800/80 flex items-center justify-between text-[10px] text-sky-400 font-semibold cursor-pointer group-hover:text-sky-300">
            <span>Inspect Reasoning</span>
            <ArrowRight className="w-3 h-3 transition-transform group-hover:translate-x-0.5" />
          </div>
        </div>
      </div>
    </div>
  );
}
