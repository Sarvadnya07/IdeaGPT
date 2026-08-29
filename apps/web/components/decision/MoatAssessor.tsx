"use client";

import React from "react";
import { Shield, Sparkles, Check, ArrowUpRight } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export interface MoatDimension {
  dimension_name: string;
  score: number;
  strength_tier: string;
  evidence: string;
  vulnerability: string;
  time_to_build_months: number;
  validation_action: string;
}

interface MoatAssessorProps {
  overallScore?: number;
  overallDefensibility?: string;
  dimensions?: MoatDimension[];
}

export const MoatAssessor: React.FC<MoatAssessorProps> = ({
  overallScore = 75,
  overallDefensibility = "HIGH_DEFENSIBILITY",
  dimensions = [
    {
      dimension_name: "Switching Costs & Workflow Lock-in",
      score: 85,
      strength_tier: "STRONG",
      evidence: "Historical evaluation trails and embedded strategy plans create high inertia against migration.",
      vulnerability: "Generic JSON/PDF export capabilities make bulk data migration technically straightforward.",
      time_to_build_months: 6,
      validation_action: "Measure 30-day retention among workspaces with 5+ generated artifacts."
    },
    {
      dimension_name: "Data Flywheel & Feedback Loops",
      score: 80,
      strength_tier: "STRONG",
      evidence: "Aggregated domain evaluations continuously refine scoring heuristics and accuracy benchmarks.",
      vulnerability: "Cold-start disadvantage against legacy enterprise market research databases.",
      time_to_build_months: 12,
      validation_action: "Benchmark scoring accuracy improvements as user evaluation volume doubles."
    },
    {
      dimension_name: "Network Effects",
      score: 65,
      strength_tier: "MODERATE",
      evidence: "Shared founder-investor report views create collaborative team value loops.",
      vulnerability: "Single-player utility must be fully compelling before team collaboration expands.",
      time_to_build_months: 9,
      validation_action: "Track invite coefficient among co-founders and advisors."
    }
  ]
}) => {
  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-4 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-emerald-400" />
            <CardTitle className="text-base font-bold text-slate-100">
              Defensibility & Moat Assessor
            </CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold text-emerald-400">Score: {overallScore}/100</span>
            <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 bg-emerald-950/20 text-[10px] uppercase font-mono">
              {overallDefensibility.replace(/_/g, " ")}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-4">
        {dimensions.map((dim, idx) => (
          <div
            key={idx}
            className="p-4 rounded-lg bg-slate-900/60 border border-slate-800/80 space-y-2"
          >
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold text-slate-200">{dim.dimension_name}</div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-slate-400">{dim.time_to_build_months} mo to build</span>
                <span className="text-xs font-mono font-bold text-indigo-400">{dim.score}/100</span>
              </div>
            </div>

            <p className="text-xs text-slate-400">{dim.evidence}</p>

            <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-t border-slate-800/60 text-[11px]">
              <div className="text-amber-400/90">Vulnerability: {dim.vulnerability}</div>
              <div className="text-emerald-400 font-medium">Test: {dim.validation_action}</div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
