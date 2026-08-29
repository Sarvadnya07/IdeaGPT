"use client";

import React, { useState } from "react";
import {
  Sliders,
  RefreshCw,
  AlertTriangle,
  ShieldCheck,
  DollarSign,
  Clock,
  Zap,
} from "lucide-react";
import { ProvenanceBadge } from "./ProvenanceBadge";

export interface ScenarioItemUI {
  variant: "BASELINE" | "OPTIMISTIC" | "CONSERVATIVE" | "ADVERSE" | string;
  runway_months: number;
  projected_time_to_mvp_months: number;
  feasibility_score: number;
  risk_profile: string;
  key_bottleneck: string;
  mitigation: string;
  provenance?: string;
}

interface ScenarioSimulatorProps {
  initialBudget?: number;
  initialTimeline?: number;
  initialBurn?: number;
  onScenarioChange?: (budget: number, timeline: number, burn: number) => void;
  className?: string;
}

export const ScenarioSimulator: React.FC<ScenarioSimulatorProps> = ({
  initialBudget = 50000,
  initialTimeline = 3,
  initialBurn = 6000,
  onScenarioChange,
  className = "",
}) => {
  const [budget, setBudget] = useState<number>(initialBudget);
  const [timeline, setTimeline] = useState<number>(initialTimeline);
  const [burn, setBurn] = useState<number>(initialBurn);

  // Deterministic local simulation calculations
  const runwayMonths = Math.max(0.1, Number((budget / burn).toFixed(1)));
  const feasibilityScore =
    runwayMonths >= timeline * 1.5
      ? 88.0
      : runwayMonths >= timeline
        ? 68.0
        : 35.0;

  const riskLevel =
    runwayMonths >= timeline * 1.5
      ? "LOW"
      : runwayMonths >= timeline
        ? "MEDIUM"
        : "HIGH";

  const handleSliderChange = (
    newBudget: number,
    newTimeline: number,
    newBurn: number,
  ) => {
    setBudget(newBudget);
    setTimeline(newTimeline);
    setBurn(newBurn);
    if (onScenarioChange) {
      onScenarioChange(newBudget, newTimeline, newBurn);
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-sm font-bold text-white flex items-center gap-2">
            <Sliders className="w-4 h-4 text-indigo-400" />
            Controlled What-If Scenario Simulator
          </h4>
          <p className="text-xs text-zinc-400 mt-0.5">
            Perturb operational parameters to test capital runway, feasibility
            elasticity, and execution risks.
          </p>
        </div>
        <ProvenanceBadge type="DETERMINISTIC_CALCULATION" />
      </div>

      {/* Interactive Sliders Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-[#0b0b0d] border border-white/10 rounded-2xl p-5">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-400 font-medium flex items-center gap-1">
              <DollarSign className="w-3.5 h-3.5 text-emerald-400" /> Available
              Budget
            </span>
            <span className="font-mono font-bold text-white">
              ${budget.toLocaleString()}
            </span>
          </div>
          <input
            type="range"
            min="10000"
            max="250000"
            step="5000"
            value={budget}
            onChange={(e) =>
              handleSliderChange(Number(e.target.value), timeline, burn)
            }
            className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-400 font-medium flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-amber-400" /> Time to MVP
            </span>
            <span className="font-mono font-bold text-white">
              {timeline} months
            </span>
          </div>
          <input
            type="range"
            min="1"
            max="12"
            step="0.5"
            value={timeline}
            onChange={(e) =>
              handleSliderChange(budget, Number(e.target.value), burn)
            }
            className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-400 font-medium flex items-center gap-1">
              <Zap className="w-3.5 h-3.5 text-rose-400" /> Monthly Burn Rate
            </span>
            <span className="font-mono font-bold text-white">
              ${burn.toLocaleString()}/mo
            </span>
          </div>
          <input
            type="range"
            min="2000"
            max="25000"
            step="1000"
            value={burn}
            onChange={(e) =>
              handleSliderChange(budget, timeline, Number(e.target.value))
            }
            className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          />
        </div>
      </div>

      {/* Output Metrics Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase text-zinc-500">
              Calculated Runway
            </span>
            <ProvenanceBadge type="DETERMINISTIC_CALCULATION" />
          </div>
          <div className="text-2xl font-black text-white font-mono">
            {runwayMonths}{" "}
            <span className="text-xs font-normal text-zinc-400">months</span>
          </div>
          <p className="text-[11px] text-zinc-400">
            {runwayMonths >= timeline
              ? "Runway extends beyond planned MVP launch."
              : "Capital exhausts before target launch."}
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase text-zinc-500">
              Simulated Feasibility
            </span>
            <ProvenanceBadge type="DETERMINISTIC_CALCULATION" />
          </div>
          <div className="text-2xl font-black text-emerald-400 font-mono">
            {feasibilityScore}%
          </div>
          <p className="text-[11px] text-zinc-400">
            Based on capital cushion vs execution duration.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase text-zinc-500">
              Risk Profile
            </span>
            <ProvenanceBadge type="DETERMINISTIC_CALCULATION" />
          </div>
          <div
            className={`text-2xl font-black font-mono ${
              riskLevel === "LOW"
                ? "text-emerald-400"
                : riskLevel === "MEDIUM"
                  ? "text-amber-400"
                  : "text-rose-400"
            }`}
          >
            {riskLevel} RISK
          </div>
          <p className="text-[11px] text-zinc-400">
            {riskLevel === "LOW"
              ? "Buffer allows error iteration."
              : "High sensitivity to launch delays."}
          </p>
        </div>
      </div>
    </div>
  );
};
