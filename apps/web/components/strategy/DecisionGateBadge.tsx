"use client";

import React from "react";
import {
  CheckCircle,
  AlertTriangle,
  HelpCircle,
  RefreshCw,
  XCircle,
} from "lucide-react";

export type DecisionGateType =
  | "GO"
  | "GO_WITH_CONDITIONS"
  | "VALIDATE_FIRST"
  | "PIVOT"
  | "STOP";

interface DecisionGateBadgeProps {
  gate: DecisionGateType | string;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export const DecisionGateBadge: React.FC<DecisionGateBadgeProps> = ({
  gate,
  className = "",
  size = "md",
}) => {
  const normGate = (gate || "VALIDATE_FIRST").toUpperCase();

  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-3 py-1 text-xs",
    lg: "px-4 py-1.5 text-sm font-bold",
  }[size];

  switch (normGate) {
    case "GO":
      return (
        <span
          className={`inline-flex items-center gap-1.5 rounded-full font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-[0_0_12px_rgba(16,185,129,0.2)] ${sizeClasses} ${className}`}
        >
          <CheckCircle className="w-3.5 h-3.5" />
          DECISION GATE: GO
        </span>
      );

    case "GO_WITH_CONDITIONS":
      return (
        <span
          className={`inline-flex items-center gap-1.5 rounded-full font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30 ${sizeClasses} ${className}`}
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          GO (WITH CONDITIONS)
        </span>
      );

    case "VALIDATE_FIRST":
      return (
        <span
          className={`inline-flex items-center gap-1.5 rounded-full font-bold bg-blue-500/15 text-blue-400 border border-blue-500/30 shadow-[0_0_12px_rgba(59,130,246,0.2)] ${sizeClasses} ${className}`}
        >
          <HelpCircle className="w-3.5 h-3.5" />
          DECISION GATE: VALIDATE FIRST
        </span>
      );

    case "PIVOT":
      return (
        <span
          className={`inline-flex items-center gap-1.5 rounded-full font-bold bg-purple-500/15 text-purple-400 border border-purple-500/30 ${sizeClasses} ${className}`}
        >
          <RefreshCw className="w-3.5 h-3.5" />
          DECISION GATE: PIVOT
        </span>
      );

    case "STOP":
    default:
      return (
        <span
          className={`inline-flex items-center gap-1.5 rounded-full font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30 ${sizeClasses} ${className}`}
        >
          <XCircle className="w-3.5 h-3.5" />
          DECISION GATE: STOP
        </span>
      );
  }
};
