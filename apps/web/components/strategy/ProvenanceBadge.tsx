"use client";

import React from "react";
import { User, Calculator, BookOpen, Sparkles, Lightbulb } from "lucide-react";

export type ProvenanceType =
  | "USER_INPUT"
  | "DETERMINISTIC_CALCULATION"
  | "RESEARCH_EVIDENCE"
  | "MODEL_INFERENCE"
  | "RECOMMENDATION";

interface ProvenanceBadgeProps {
  type: ProvenanceType | string;
  className?: string;
}

export const ProvenanceBadge: React.FC<ProvenanceBadgeProps> = ({ type, className = "" }) => {
  const normType = (type || "MODEL_INFERENCE").toUpperCase();

  switch (normType) {
    case "USER_INPUT":
      return (
        <span
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 ${className}`}
        >
          <User className="w-2.5 h-2.5" /> USER INPUT
        </span>
      );

    case "DETERMINISTIC_CALCULATION":
      return (
        <span
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 ${className}`}
        >
          <Calculator className="w-2.5 h-2.5" /> DETERMINISTIC CALCULATION
        </span>
      );

    case "RESEARCH_EVIDENCE":
      return (
        <span
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 ${className}`}
        >
          <BookOpen className="w-2.5 h-2.5" /> RESEARCH EVIDENCE
        </span>
      );

    case "RECOMMENDATION":
      return (
        <span
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-500/10 text-purple-400 border border-purple-500/20 ${className}`}
        >
          <Lightbulb className="w-2.5 h-2.5" /> STRATEGIC RECOMMENDATION
        </span>
      );

    case "MODEL_INFERENCE":
    default:
      return (
        <span
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-500/10 text-slate-400 border border-slate-500/20 ${className}`}
        >
          <Sparkles className="w-2.5 h-2.5" /> MODEL INFERENCE
        </span>
      );
  }
};
