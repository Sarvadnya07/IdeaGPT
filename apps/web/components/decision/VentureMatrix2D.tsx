"use client";

import React from "react";
import { Grid, Sparkles, Target, Compass } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export interface VenturePoint {
  idea_id: string;
  idea_title: string;
  project_title: string;
  x_attractiveness_score: number;
  y_execution_risk_score: number;
  decision_gate: string;
  quadrant: string;
}

interface VentureMatrix2DProps {
  points?: VenturePoint[];
}

export const VentureMatrix2D: React.FC<VentureMatrix2DProps> = ({
  points = [
    {
      idea_id: "p-1",
      idea_title: "IdeaGPT Platform",
      project_title: "AI Decision Intelligence",
      x_attractiveness_score: 85,
      y_execution_risk_score: 28,
      decision_gate: "GO",
      quadrant: "High Value / Low Risk"
    },
    {
      idea_id: "p-2",
      idea_title: "Legacy Workflow Automation",
      project_title: "B2B Ops",
      x_attractiveness_score: 62,
      y_execution_risk_score: 48,
      decision_gate: "VALIDATE_FIRST",
      quadrant: "Low Value / High Risk"
    }
  ]
}) => {
  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-4 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Compass className="h-5 w-5 text-indigo-400" />
            <CardTitle className="text-base font-bold text-slate-100">
              2D Venture Matrix (Attractiveness vs Execution Risk)
            </CardTitle>
          </div>
          <span className="text-[10px] font-mono uppercase bg-slate-800 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
            {points.length} Ventures Plotted
          </span>
        </div>
      </CardHeader>

      <CardContent className="p-6">
        {/* 2D Matrix Canvas */}
        <div className="relative h-72 w-full rounded-xl bg-slate-900/80 border border-slate-800 p-4 overflow-hidden flex flex-col justify-between">
          {/* Axis Labels */}
          <div className="absolute top-2 left-3 text-[10px] font-mono text-rose-400 font-bold uppercase">
            ▲ High Execution Risk (100)
          </div>
          <div className="absolute bottom-2 left-3 text-[10px] font-mono text-emerald-400 font-bold uppercase">
            ▼ Low Execution Risk (0)
          </div>
          <div className="absolute bottom-2 right-3 text-[10px] font-mono text-indigo-400 font-bold uppercase">
            High Attractiveness (100) ▶
          </div>

          {/* Center Quadrant Dividers */}
          <div className="absolute inset-x-0 top-1/2 border-t border-dashed border-slate-800/80" />
          <div className="absolute inset-y-0 left-1/2 border-l border-dashed border-slate-800/80" />

          {/* Quadrant Background Watermarks */}
          <div className="absolute top-4 right-4 text-xs font-semibold text-slate-800 uppercase tracking-widest select-none">
            High Potential / High Risk
          </div>
          <div className="absolute bottom-6 right-4 text-xs font-semibold text-emerald-950/60 uppercase tracking-widest select-none">
            ★ Sweet Spot (Venture Ready)
          </div>
          <div className="absolute top-4 left-4 text-xs font-semibold text-slate-800 uppercase tracking-widest select-none">
            Avoid (High Risk / Low Return)
          </div>
          <div className="absolute bottom-6 left-4 text-xs font-semibold text-slate-800 uppercase tracking-widest select-none">
            Niche / Lifestyle
          </div>

          {/* Plotted Points */}
          {points.map((pt) => {
            const leftPct = Math.min(92, Math.max(8, pt.x_attractiveness_score));
            // Invert y so 0 is at bottom, 100 at top
            const bottomPct = Math.min(88, Math.max(12, 100 - pt.y_execution_risk_score));
            return (
              <div
                key={pt.idea_id}
                style={{ left: `${leftPct}%`, bottom: `${bottomPct}%` }}
                className="absolute transform -translate-x-1/2 translate-y-1/2 group cursor-pointer"
              >
                <div className="relative flex items-center justify-center">
                  <div className="h-4 w-4 rounded-full bg-indigo-500 border-2 border-slate-950 animate-ping absolute opacity-30" />
                  <div className="h-3.5 w-3.5 rounded-full bg-indigo-400 border border-slate-950 shadow-md group-hover:scale-125 transition-transform" />
                  
                  {/* Tooltip on hover */}
                  <div className="absolute bottom-full mb-1.5 hidden group-hover:flex flex-col items-center z-20 whitespace-nowrap">
                    <div className="bg-slate-900 border border-slate-700 text-slate-100 text-xs py-1 px-2.5 rounded shadow-xl space-y-0.5">
                      <div className="font-bold text-slate-200">{pt.idea_title}</div>
                      <div className="text-[10px] text-slate-400">
                        Score: {pt.x_attractiveness_score} | Risk: {pt.y_execution_risk_score} | Gate: {pt.decision_gate}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
