"use client";

import React from "react";
import { Scale, CheckCircle, AlertCircle, HelpCircle } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export interface RegulatoryFramework {
  framework_name: string;
  relevance: string;
  jurisdiction: string;
  key_obligation: string;
  impact_level: string;
  citation_source: string;
  confidence: string;
}

interface RegulatoryRadarProps {
  frameworks?: RegulatoryFramework[];
  industry?: string;
}

export const RegulatoryRadar: React.FC<RegulatoryRadarProps> = ({
  frameworks = [
    {
      framework_name: "GDPR (General Data Protection Regulation)",
      relevance: "POTENTIALLY_RELEVANT",
      jurisdiction: "European Union / Global",
      key_obligation: "Explicit consent, right to be forgotten, and AI data transparency.",
      impact_level: "HIGH",
      citation_source: "EU Directive 2016/679",
      confidence: "HIGH"
    },
    {
      framework_name: "EU AI Act",
      relevance: "NEEDS_VERIFICATION",
      jurisdiction: "European Union",
      key_obligation: "Mandatory transparency for generative AI; safety compliance for high-risk systems.",
      impact_level: "HIGH",
      citation_source: "EU Regulation 2024/1689",
      confidence: "HIGH"
    },
    {
      framework_name: "SOC 2 Type II",
      relevance: "POTENTIALLY_RELEVANT",
      jurisdiction: "Global Enterprise",
      key_obligation: "Security, availability, and confidentiality audit readiness.",
      impact_level: "HIGH",
      citation_source: "AICPA Trust Services Criteria",
      confidence: "HIGH"
    },
    {
      framework_name: "PCI-DSS v4.0",
      relevance: "POTENTIALLY_RELEVANT",
      jurisdiction: "Global Payments",
      key_obligation: "Delegated payment card processing via certified gateway (Stripe).",
      impact_level: "MEDIUM",
      citation_source: "PCI Security Standards Council",
      confidence: "HIGH"
    }
  ],
  industry = "B2B SaaS"
}) => {
  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-4 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Scale className="h-5 w-5 text-indigo-400" />
            <CardTitle className="text-base font-bold text-slate-100">
              Regulatory & Compliance Radar
            </CardTitle>
          </div>
          <span className="text-[10px] font-mono uppercase bg-slate-800 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
            Sector: {industry}
          </span>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-4">
        {frameworks.map((fw, idx) => (
          <div
            key={idx}
            className="p-4 rounded-lg bg-slate-900/60 border border-slate-800/80 space-y-2"
          >
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                {fw.relevance === "POTENTIALLY_RELEVANT" ? (
                  <AlertCircle className="h-4 w-4 text-amber-400" />
                ) : fw.relevance === "NEEDS_VERIFICATION" ? (
                  <HelpCircle className="h-4 w-4 text-sky-400" />
                ) : (
                  <CheckCircle className="h-4 w-4 text-emerald-400" />
                )}
                {fw.framework_name}
              </div>
              <Badge
                variant="outline"
                className={`text-[10px] uppercase font-mono ${
                  fw.impact_level === "HIGH"
                    ? "border-rose-500/30 text-rose-400 bg-rose-950/20"
                    : "border-sky-500/30 text-sky-400 bg-sky-950/20"
                }`}
              >
                Impact: {fw.impact_level}
              </Badge>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">{fw.key_obligation}</p>

            <div className="pt-2 flex items-center justify-between border-t border-slate-800/60 text-[11px] text-slate-500">
              <div>Jurisdiction: <span className="text-slate-400">{fw.jurisdiction}</span></div>
              <div>Source: <span className="text-slate-400">{fw.citation_source}</span></div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
