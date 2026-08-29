"use client";

import React from "react";
import { AlertCircle, ShieldAlert, CheckCircle2, FileText, ExternalLink } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export interface RedFlag {
  id: string;
  category: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  title: string;
  claim_analysis: string;
  evidence_citation?: string;
  confidence: string;
  recommended_validation: string;
}

interface InvestorRedFlagsProps {
  redFlags?: RedFlag[];
  overallReadiness?: string;
}

export const InvestorRedFlags: React.FC<InvestorRedFlagsProps> = ({
  redFlags = [
    {
      id: "rf-1",
      category: "REGULATORY",
      severity: "HIGH",
      title: "Statutory Compliance Barrier (HIPAA / GDPR)",
      claim_analysis: "Healthcare and Fintech products require strict data segregation and Business Associate Agreements.",
      evidence_citation: "45 CFR Part 160 & EU GDPR Directive",
      confidence: "HIGH",
      recommended_validation: "Engage specialized healthcare counsel and obtain SOC 2 audit readiness assessment."
    },
    {
      id: "rf-2",
      category: "CAPITAL",
      severity: "MEDIUM",
      title: "AI Inference Cost Compression",
      claim_analysis: "Unmetered user queries without caching can degrade gross margin below 70%.",
      evidence_citation: "LLM Provider Pricing Matrix",
      confidence: "HIGH",
      recommended_validation: "Implement 24h deterministic response caching and smaller model fallbacks."
    },
    {
      id: "rf-3",
      category: "DEFENSIBILITY",
      severity: "MEDIUM",
      title: "Incumbent Distribution Advantage",
      claim_analysis: "Established platforms already control enterprise distribution.",
      evidence_citation: "Competitor Market Landscape",
      confidence: "MEDIUM",
      recommended_validation: "Focus initial GTM on underserved niche verticals."
    }
  ],
  overallReadiness = "PROCEED_WITH_CAUTION"
}) => {
  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-4 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-rose-400" />
            <CardTitle className="text-base font-bold text-slate-100">
              Investor Red-Flag Scanner
            </CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono uppercase bg-slate-800 text-rose-400 px-2 py-0.5 rounded border border-rose-500/20">
              {overallReadiness}
            </span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-4">
        {redFlags.map((flag) => (
          <div
            key={flag.id}
            className="p-4 rounded-lg bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition-colors space-y-2"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${
                  flag.severity === "CRITICAL" ? "bg-rose-500" : flag.severity === "HIGH" ? "bg-amber-500" : "bg-sky-500"
                }`} />
                <span className="text-sm font-semibold text-slate-200">{flag.title}</span>
              </div>
              <Badge
                variant="outline"
                className={`text-[10px] uppercase font-mono ${
                  flag.severity === "CRITICAL"
                    ? "border-rose-500/30 text-rose-400 bg-rose-950/20"
                    : flag.severity === "HIGH"
                    ? "border-amber-500/30 text-amber-400 bg-amber-950/20"
                    : "border-sky-500/30 text-sky-400 bg-sky-950/20"
                }`}
              >
                {flag.severity}
              </Badge>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">{flag.claim_analysis}</p>

            <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-t border-slate-800/60 text-[11px]">
              <div className="text-slate-500 flex items-center gap-1.5">
                <FileText className="h-3.5 w-3.5 text-slate-400" />
                <span>Source: {flag.evidence_citation || "Grounded Research"}</span>
              </div>
              <div className="text-indigo-400 font-medium flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Fix: {flag.recommended_validation}</span>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
