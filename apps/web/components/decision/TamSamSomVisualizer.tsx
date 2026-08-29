"use client";

import React from "react";
import { PieChart, Globe, DollarSign, ArrowUpRight, TrendingUp } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export interface MarketLayer {
  layer_name: string;
  value_usd: string;
  description: string;
  methodology: string;
  classification: "FACT" | "ESTIMATE";
  source_citation?: string;
}

interface TamSamSomVisualizerProps {
  tam?: MarketLayer;
  sam?: MarketLayer;
  som?: MarketLayer;
  cagr?: string;
  industry?: string;
}

export const TamSamSomVisualizer: React.FC<TamSamSomVisualizerProps> = ({
  tam = {
    layer_name: "Total Addressable Market (TAM)",
    value_usd: "$4.2B",
    description: "Worldwide enterprise spend on idea validation, product strategy, and market research tools.",
    methodology: "Top-down market sizing based on global SaaS analytics spending reports.",
    classification: "FACT",
    source_citation: "Gartner & Statista Market Intelligence"
  },
  sam = {
    layer_name: "Serviceable Addressable Market (SAM)",
    value_usd: "$850M",
    description: "English-speaking tech startups, venture studios, and early-stage founders.",
    methodology: "Bottom-up: ~500k target startup teams × $1,700 annual ARPU.",
    classification: "ESTIMATE",
    source_citation: "US & EU Census Business Registries"
  },
  som = {
    layer_name: "Serviceable Obtainable Market (SOM)",
    value_usd: "$45M",
    description: "Realistic 3-year market capture target (5% of SAM) via product-led growth.",
    methodology: "Capacity-constrained inbound funnel model.",
    classification: "ESTIMATE",
    source_citation: "IdeaGPT GTM Execution Model"
  },
  cagr = "14.5%",
  industry = "B2B AI Software"
}) => {
  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-4 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Globe className="h-5 w-5 text-indigo-400" />
            <CardTitle className="text-base font-bold text-slate-100">
              TAM / SAM / SOM Market Sizing
            </CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-emerald-400 flex items-center gap-1">
              <TrendingUp className="h-3.5 w-3.5" /> CAGR: {cagr}
            </span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Visual Concentric Rings representation */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* TAM Card */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 relative overflow-hidden">
            <div className="text-[11px] font-bold uppercase text-indigo-400">Total Addressable (TAM)</div>
            <div className="text-2xl font-black text-slate-100">{tam.value_usd}</div>
            <p className="text-xs text-slate-400">{tam.description}</p>
            <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-500 flex items-center justify-between">
              <span>{tam.classification}</span>
              <span className="truncate max-w-[140px] text-slate-400">{tam.source_citation}</span>
            </div>
          </div>

          {/* SAM Card */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 relative overflow-hidden">
            <div className="text-[11px] font-bold uppercase text-sky-400">Serviceable (SAM)</div>
            <div className="text-2xl font-black text-slate-100">{sam.value_usd}</div>
            <p className="text-xs text-slate-400">{sam.description}</p>
            <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-500 flex items-center justify-between">
              <span>{sam.classification}</span>
              <span className="truncate max-w-[140px] text-slate-400">{sam.source_citation}</span>
            </div>
          </div>

          {/* SOM Card */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 relative overflow-hidden">
            <div className="text-[11px] font-bold uppercase text-emerald-400">Obtainable (SOM)</div>
            <div className="text-2xl font-black text-emerald-400">{som.value_usd}</div>
            <p className="text-xs text-slate-400">{som.description}</p>
            <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-500 flex items-center justify-between">
              <span>{som.classification}</span>
              <span className="truncate max-w-[140px] text-slate-400">{som.source_citation}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
