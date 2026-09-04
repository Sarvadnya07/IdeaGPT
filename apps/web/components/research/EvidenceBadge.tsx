"use client";

import React from "react";
import {
  CheckCircle2,
  Calculator,
  Sparkles,
  HelpCircle,
  AlertTriangle,
  Lightbulb,
} from "lucide-react";

export type EvidenceType =
  | "FACT"
  | "ESTIMATE"
  | "INFERENCE"
  | "RECOMMENDATION"
  | "UNKNOWN"
  | "CONFLICTING_EVIDENCE";

interface EvidenceBadgeProps {
  type: EvidenceType | string;
  className?: string;
}

export const EvidenceBadge: React.FC<EvidenceBadgeProps> = ({
  type,
  className = "",
}) => {
  const normType = (type || "INFERENCE").toUpperCase();

  switch (normType) {
    case "FACT":
      return (
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 ${className}`}
        >
          <CheckCircle2 className="w-3 h-3" />
          FACT (VERIFIED)
        </span>
      );

    case "ESTIMATE":
      return (
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 ${className}`}
        >
          <Calculator className="w-3 h-3" />
          ESTIMATE
        </span>
      );

    case "INFERENCE":
      return (
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 ${className}`}
        >
          <Sparkles className="w-3 h-3" />
          INFERENCE
        </span>
      );

    case "RECOMMENDATION":
      return (
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20 ${className}`}
        >
          <Lightbulb className="w-3 h-3" />
          RECOMMENDATION
        </span>
      );

    case "CONFLICTING_EVIDENCE":
      return (
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 ${className}`}
        >
          <AlertTriangle className="w-3 h-3" />
          CONFLICTING SOURCES
        </span>
      );

    case "UNKNOWN":
    default:
      return (
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20 ${className}`}
        >
          <HelpCircle className="w-3 h-3" />
          UNKNOWN / UNRESOLVED
        </span>
      );
  }
};
