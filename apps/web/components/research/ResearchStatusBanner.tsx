"use client";

import React from "react";
import {
  Loader2,
  CheckCircle2,
  AlertTriangle,
  Search,
  Info,
} from "lucide-react";

export type ResearchStatus =
  | "RESEARCHING"
  | "COLLECTING"
  | "ANALYZING"
  | "COMPLETED"
  | "PARTIAL"
  | "RESEARCH_UNAVAILABLE"
  | "FAILED";

interface ResearchStatusBannerProps {
  status: ResearchStatus | string;
  sourceCount?: number;
  className?: string;
}

export const ResearchStatusBanner: React.FC<ResearchStatusBannerProps> = ({
  status,
  sourceCount = 0,
  className = "",
}) => {
  const normStatus = (status || "COMPLETED").toUpperCase();

  if (
    normStatus === "RESEARCHING" ||
    normStatus === "COLLECTING" ||
    normStatus === "ANALYZING"
  ) {
    return (
      <div
        className={`flex items-center gap-3 px-4 py-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300 text-sm ${className}`}
      >
        <Loader2 className="w-4 h-4 animate-spin text-blue-400 flex-shrink-0" />
        <div className="flex-1">
          <span className="font-semibold">Conducting Deep Web Research: </span>
          <span className="text-slate-300">
            {normStatus === "RESEARCHING" &&
              "Querying verified domain indexes via Tavily AI..."}
            {normStatus === "COLLECTING" &&
              `Collecting and deduplicating ${sourceCount} web citations...`}
            {normStatus === "ANALYZING" &&
              "Validating factual claims and synthesizing evidence..."}
          </span>
        </div>
      </div>
    );
  }

  if (normStatus === "RESEARCH_UNAVAILABLE") {
    return (
      <div
        className={`flex items-center gap-3 px-4 py-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-sm ${className}`}
      >
        <Info className="w-4 h-4 text-amber-400 flex-shrink-0" />
        <div className="flex-1">
          <span className="font-semibold">
            Research Provider Offline (Non-Grounded Mode):{" "}
          </span>
          <span className="text-slate-300">
            External search API is currently unavailable. Analysis relies on
            deterministic rule models and internal LLM memory. Factual claims
            are labeled as ESTIMATE or UNKNOWN.
          </span>
        </div>
      </div>
    );
  }

  if (normStatus === "FAILED") {
    return (
      <div
        className={`flex items-center gap-3 px-4 py-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm ${className}`}
      >
        <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
        <div className="flex-1">
          <span className="font-semibold">Research Error: </span>
          <span className="text-slate-300">
            Web search pipeline encountered a transient failure. Please retry or
            provide a BYOK Tavily API key.
          </span>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex items-center justify-between px-4 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-medium ${className}`}
    >
      <div className="flex items-center gap-2">
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
        <span>Evidence-Grounded Analysis Active</span>
      </div>
      <div className="flex items-center gap-1.5 text-slate-400">
        <Search className="w-3 h-3" />
        <span>{sourceCount} Verified Sources Cited</span>
      </div>
    </div>
  );
};
