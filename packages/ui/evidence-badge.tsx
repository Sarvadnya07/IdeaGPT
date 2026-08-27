import React from "react";
import { Check, HelpCircle, Sparkles, TrendingUp, AlertTriangle } from "lucide-react";

export type EvidenceType = "FACT" | "ESTIMATE" | "INFERENCE" | "RECOMMENDATION" | "UNKNOWN" | "RISK";

interface EvidenceBadgeProps {
  type: EvidenceType;
  label?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function EvidenceBadge({
  type,
  label,
  size = "md",
  className = "",
}: EvidenceBadgeProps) {
  const sizeStyles = {
    sm: "px-2 py-0.5 text-[9px] gap-1",
    md: "px-2.5 py-1 text-[10px] gap-1.5",
    lg: "px-3 py-1.5 text-xs gap-2",
  };

  const displayText = label || type;

  switch (type) {
    case "FACT":
      return (
        <span
          className={`inline-flex items-center font-bold tracking-wider uppercase text-white bg-[#0284C7] shadow-[0_0_12px_rgba(2,132,199,0.35)] rounded-md ${sizeStyles[size]} ${className}`}
        >
          <Check className="w-3 h-3 stroke-[3]" />
          <span>{displayText}</span>
        </span>
      );

    case "ESTIMATE":
      return (
        <span
          className={`inline-flex items-center font-bold tracking-wider uppercase text-amber-300 bg-amber-500/15 border border-amber-500/40 relative overflow-hidden rounded-md ${sizeStyles[size]} ${className}`}
          style={{
            backgroundImage:
              "repeating-linear-gradient(45deg, rgba(245, 158, 11, 0.08), rgba(245, 158, 11, 0.08) 4px, transparent 4px, transparent 8px)",
          }}
        >
          <TrendingUp className="w-3 h-3 stroke-[2.5]" />
          <span>{displayText}</span>
        </span>
      );

    case "INFERENCE":
      return (
        <span
          className={`inline-flex items-center font-bold tracking-wider uppercase text-blue-300 bg-blue-500/10 border border-dashed border-blue-400/60 rounded-md ${sizeStyles[size]} ${className}`}
        >
          <Sparkles className="w-3 h-3 text-blue-400 stroke-[2]" />
          <span>{displayText}</span>
        </span>
      );

    case "RECOMMENDATION":
      return (
        <span
          className={`inline-flex items-center font-bold tracking-wider uppercase text-zinc-950 bg-[#00C29A] shadow-[0_0_15px_rgba(0,194,154,0.4)] rounded-md ${sizeStyles[size]} ${className}`}
        >
          <Sparkles className="w-3 h-3 fill-zinc-950 stroke-[2]" />
          <span>{displayText}</span>
        </span>
      );

    case "RISK":
      return (
        <span
          className={`inline-flex items-center font-bold tracking-wider uppercase text-red-300 bg-red-500/15 border border-red-500/40 rounded-md ${sizeStyles[size]} ${className}`}
        >
          <AlertTriangle className="w-3 h-3 text-red-400 stroke-[2.5]" />
          <span>{displayText}</span>
        </span>
      );

    case "UNKNOWN":
    default:
      return (
        <span
          className={`inline-flex items-center font-bold tracking-wider uppercase text-zinc-400 bg-zinc-800/80 border border-zinc-700/60 rounded-md ${sizeStyles[size]} ${className}`}
        >
          <HelpCircle className="w-3 h-3 text-zinc-400 stroke-[2]" />
          <span>{displayText}</span>
        </span>
      );
  }
}
