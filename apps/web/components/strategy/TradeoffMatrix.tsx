"use client";

import React from "react";
import {
  Scale,
  ArrowRightLeft,
  ShieldAlert,
  Sparkles,
  CheckCircle2,
} from "lucide-react";
import { ProvenanceBadge } from "./ProvenanceBadge";

export interface TradeoffItemUI {
  id: string;
  dimension: string;
  option_a_name: string;
  option_b_name: string;
  difference: string;
  consequence: string;
  reversibility:
    | "REVERSIBLE"
    | "PARTIALLY_REVERSIBLE"
    | "HARD_TO_REVERSE"
    | string;
  evidence_citations?: string[];
  confidence?: string;
  provenance?: string;
}

interface TradeoffMatrixProps {
  tradeoffs: TradeoffItemUI[];
  className?: string;
}

export const TradeoffMatrix: React.FC<TradeoffMatrixProps> = ({
  tradeoffs,
  className = "",
}) => {
  if (!tradeoffs || tradeoffs.length === 0) {
    return (
      <div className="text-xs text-slate-500 italic p-4 text-center border border-zinc-800 rounded-xl">
        No strategic trade-offs recorded.
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-sm font-bold text-white flex items-center gap-2">
            <Scale className="w-4 h-4 text-indigo-400" />
            Strategic Trade-Off & Reversibility Analysis
          </h4>
          <p className="text-xs text-zinc-400 mt-0.5">
            Explicit evaluation of strategic alternatives, opportunity costs,
            and reversal friction.
          </p>
        </div>
        <ProvenanceBadge type="MODEL_INFERENCE" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {tradeoffs.map((item, idx) => (
          <div
            key={item.id || idx}
            className="p-5 rounded-2xl bg-[#0b0b0d] border border-white/10 space-y-4 shadow-[0_4px_20px_rgba(0,0,0,0.3)]"
          >
            <div className="flex items-start justify-between gap-2 border-b border-white/5 pb-3">
              <div>
                <span className="text-[10px] font-bold uppercase text-zinc-500 tracking-wider">
                  Dimension
                </span>
                <h5 className="text-xs font-bold text-white mt-0.5">
                  {item.dimension}
                </h5>
              </div>

              <span
                className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                  item.reversibility === "REVERSIBLE"
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    : item.reversibility === "PARTIALLY_REVERSIBLE"
                      ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                }`}
              >
                {item.reversibility.replace("_", " ")}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-3 rounded-lg bg-slate-900/60 border border-white/5 space-y-1">
                <span className="text-[10px] font-bold text-indigo-400 uppercase">
                  Option A
                </span>
                <p className="text-zinc-200 font-semibold text-[11px]">
                  {item.option_a_name}
                </p>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/60 border border-white/5 space-y-1">
                <span className="text-[10px] font-bold text-purple-400 uppercase">
                  Option B
                </span>
                <p className="text-zinc-200 font-semibold text-[11px]">
                  {item.option_b_name}
                </p>
              </div>
            </div>

            <div className="space-y-2 text-xs">
              <div>
                <span className="text-[10px] font-bold uppercase text-zinc-400">
                  Core Differential
                </span>
                <p className="text-zinc-300 mt-0.5 leading-relaxed">
                  {item.difference}
                </p>
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase text-amber-400">
                  Strategic Consequence
                </span>
                <p className="text-zinc-300 mt-0.5 leading-relaxed">
                  {item.consequence}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
