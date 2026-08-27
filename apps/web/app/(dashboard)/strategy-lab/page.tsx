"use client";

import React, { useState } from "react";
import { useProjects } from "../../../hooks/useProjects";
import { useApiClient } from "@/lib/api/client";
import { toast } from "sonner";
import {
  Compass,
  Zap,
  Shield,
  Tag,
  Share2,
  Loader2,
  RefreshCw,
  Target,
  BarChart3,
  Layers,
} from "lucide-react";

interface PorterForce {
  force_name: string;
  intensity: "LOW" | "MEDIUM" | "HIGH";
  analysis: string;
  strategic_defense: string;
}

interface BlueOcean {
  eliminate: string[];
  reduce: string[];
  raise: string[];
  create: string[];
}

interface DefensibilityMoat {
  network_effects: number;
  switching_costs: number;
  data_flywheel: number;
  brand_and_distribution: number;
}

interface PricingTier {
  tier_name: string;
  price_monthly_usd: string;
  target_persona: string;
  core_features: string[];
  estimated_gross_margin: string;
}

interface GtmGrowthEngine {
  primary_loop: string;
  viral_coefficient_target: string;
  payback_period_months: string;
}

interface StrategyLabResult {
  porter_five_forces: PorterForce[];
  blue_ocean_strategy: BlueOcean;
  defensibility_moat_breakdown: DefensibilityMoat;
  pricing_model_matrix: PricingTier[];
  gtm_growth_engine: GtmGrowthEngine;
}

export default function StrategyLabPage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects();
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const activeProjectId = selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<StrategyLabResult | null>(null);

  const handleGenerate = async () => {
    if (!activeProject) {
      toast.error("Please select a project first.");
      return;
    }
    setIsGenerating(true);
    try {
      const res = await api.post<StrategyLabResult>("/ai/labs/strategy", {
        title: activeProject.title,
        category: activeProject.category || "B2B SaaS",
        competitors: "Legacy ERPs and point solution spreadsheets",
        value_proposition: activeProject.description || "10x faster automation with domain-tailored AI models",
      });
      setResult(res.data);
      toast.success("Strategic Competitive Analysis synthesized successfully!");
    } catch (err: any) {
      toast.error("Failed to generate strategy analysis");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-8 py-4 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-zinc-900 pb-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 uppercase tracking-widest gap-1.5">
              <Compass className="w-3 h-3" /> Strategy & Moat Lab
            </span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            {activeProject?.title || "Competitive Strategy Analysis"}
          </h1>
          <p className="text-xs text-zinc-500 max-w-2xl leading-relaxed">
            Porter&apos;s Five Forces micro-economics, Blue Ocean strategy canvas, defensibility moat quantification,
            and growth loop monetization modeling.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3 shrink-0">
          <select
            value={activeProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="bg-[#0b0b0d] border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-500"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title}
              </option>
            ))}
          </select>
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !activeProject}
            className="flex items-center gap-2 px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)] cursor-pointer"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> Synthesizing Strategy...
              </>
            ) : (
              <>
                <RefreshCw className="w-3.5 h-3.5" /> Analyze Strategy
              </>
            )}
          </button>
        </div>
      </div>

      {result ? (
        <div className="space-y-6">
          {/* Moat Breakdown & Growth Loop Top Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Defensibility Moat Scores */}
            <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 md:col-span-2 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">Defensibility Moat Quantification</h3>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
                <div className="p-3.5 rounded-xl bg-black/40 border border-zinc-900 text-center">
                  <span className="text-xl font-bold text-cyan-400 block">{result.defensibility_moat_breakdown.network_effects}</span>
                  <span className="text-[10px] text-zinc-500 uppercase font-semibold">Network Effects</span>
                </div>
                <div className="p-3.5 rounded-xl bg-black/40 border border-zinc-900 text-center">
                  <span className="text-xl font-bold text-emerald-400 block">{result.defensibility_moat_breakdown.switching_costs}</span>
                  <span className="text-[10px] text-zinc-500 uppercase font-semibold">Switching Friction</span>
                </div>
                <div className="p-3.5 rounded-xl bg-black/40 border border-zinc-900 text-center">
                  <span className="text-xl font-bold text-purple-400 block">{result.defensibility_moat_breakdown.data_flywheel}</span>
                  <span className="text-[10px] text-zinc-500 uppercase font-semibold">Data Flywheel</span>
                </div>
                <div className="p-3.5 rounded-xl bg-black/40 border border-zinc-900 text-center">
                  <span className="text-xl font-bold text-amber-400 block">{result.defensibility_moat_breakdown.brand_and_distribution}</span>
                  <span className="text-[10px] text-zinc-500 uppercase font-semibold">Brand / GTM</span>
                </div>
              </div>
            </div>

            {/* Growth Engine Card */}
            <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-3">
              <div className="flex items-center gap-2">
                <Share2 className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">GTM Growth Engine</h3>
              </div>
              <p className="text-xs text-zinc-300 leading-relaxed">{result.gtm_growth_engine.primary_loop}</p>
              <div className="flex justify-between pt-2 border-t border-zinc-900 text-xs font-mono">
                <span className="text-zinc-500">Viral Coeff: <strong className="text-emerald-400">{result.gtm_growth_engine.viral_coefficient_target}</strong></span>
                <span className="text-zinc-500">Payback: <strong className="text-cyan-400">{result.gtm_growth_engine.payback_period_months} mo</strong></span>
              </div>
            </div>
          </div>

          {/* Blue Ocean Strategy Canvas Matrix */}
          <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-cyan-400" />
              <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">Blue Ocean Strategy Matrix (ERRC Framework)</h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-red-950/20 border border-red-900/30 space-y-2">
                <span className="font-bold text-red-400 text-[11px] uppercase tracking-wider block">🚫 Eliminate</span>
                <ul className="text-[11px] text-zinc-400 list-disc list-inside space-y-1">
                  {result.blue_ocean_strategy.eliminate.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-900/30 space-y-2">
                <span className="font-bold text-amber-400 text-[11px] uppercase tracking-wider block">📉 Reduce</span>
                <ul className="text-[11px] text-zinc-400 list-disc list-inside space-y-1">
                  {result.blue_ocean_strategy.reduce.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-900/30 space-y-2">
                <span className="font-bold text-indigo-400 text-[11px] uppercase tracking-wider block">📈 Raise</span>
                <ul className="text-[11px] text-zinc-400 list-disc list-inside space-y-1">
                  {result.blue_ocean_strategy.raise.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-900/30 space-y-2">
                <span className="font-bold text-emerald-400 text-[11px] uppercase tracking-wider block">✨ Create</span>
                <ul className="text-[11px] text-zinc-400 list-disc list-inside space-y-1">
                  {result.blue_ocean_strategy.create.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Porter's Five Forces Analysis */}
          <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">Porter&apos;s Five Forces Analysis</h3>
            </div>
            <div className="space-y-3">
              {result.porter_five_forces.map((force, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-black/40 border border-zinc-900 space-y-2 text-xs">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-white">{force.force_name}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        force.intensity === "HIGH"
                          ? "bg-red-500/20 text-red-400"
                          : force.intensity === "MEDIUM"
                          ? "bg-amber-500/20 text-amber-400"
                          : "bg-emerald-500/20 text-emerald-400"
                      }`}
                    >
                      {force.intensity} Pressure
                    </span>
                  </div>
                  <p className="text-zinc-400 text-[11px] leading-relaxed">{force.analysis}</p>
                  <div className="pt-2 border-t border-zinc-900/60 flex items-start gap-1.5 text-[11px]">
                    <span className="font-bold text-cyan-400 shrink-0">Defense:</span>
                    <span className="text-zinc-300">{force.strategic_defense}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Pricing Tiers Matrix */}
          <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
            <div className="flex items-center gap-2">
              <Tag className="w-4 h-4 text-emerald-400" />
              <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">Monetization & Pricing Tiers</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {result.pricing_model_matrix.map((tier, idx) => (
                <div key={idx} className="p-5 rounded-xl bg-black/40 border border-zinc-900 space-y-3 text-xs">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-bold text-white text-sm">{tier.tier_name}</h4>
                      <span className="text-[11px] text-zinc-500 block">{tier.target_persona}</span>
                    </div>
                    <span className="text-lg font-bold text-emerald-400 font-mono">{tier.price_monthly_usd}</span>
                  </div>
                  <ul className="text-[11px] text-zinc-400 list-disc list-inside space-y-1 pt-2 border-t border-zinc-900">
                    {tier.core_features.map((feat, fIdx) => (
                      <li key={fIdx}>{feat}</li>
                    ))}
                  </ul>
                  <span className="text-[10px] font-mono text-zinc-500 block pt-2">
                    Estimated Gross Margin: <strong className="text-zinc-300">{tier.estimated_gross_margin}</strong>
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20 border border-zinc-900/60 rounded-2xl bg-[#0b0b0d] text-center p-8 space-y-4">
          <Compass className="w-12 h-12 text-zinc-700 mb-2" />
          <h3 className="text-lg font-bold text-white">No Strategy Analysis Formulated</h3>
          <p className="text-xs text-zinc-500 max-w-md leading-relaxed">
            Click &quot;Analyze Strategy&quot; to synthesize Porter&apos;s 5 Forces, Blue Ocean Canvas, and defensibility moats.
          </p>
        </div>
      )}
    </div>
  );
}
