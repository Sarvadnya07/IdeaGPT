"use client";

import React, { useState } from "react";
import { Server, Cloud, Cpu, Database, HardDrive, DollarSign } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export const CloudCostEstimator: React.FC = () => {
  const [mau, setMau] = useState<number>(10000);
  const [reqs, setReqs] = useState<number>(500000);
  const [dbGb, setDbGb] = useState<number>(20);
  const [tokensM, setTokensM] = useState<number>(10);

  // Deterministic multi-cloud pricing
  const aiCost = (tokensM * 0.60).toFixed(2);
  const vercelCost = (20 + (reqs * 0.00005 * 0.15)).toFixed(2);
  const supaCost = (25 + Math.max(0, (dbGb - 8) * 0.125)).toFixed(2);
  const awsCost = (40 + Math.max(35, dbGb * 1.5) + 32).toFixed(2);
  const cfCost = (5 + 0.15).toFixed(2);

  const recommendedTotal = (parseFloat(vercelCost) + parseFloat(supaCost) + parseFloat(aiCost)).toFixed(2);

  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-4 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cloud className="h-5 w-5 text-indigo-400" />
            <CardTitle className="text-base font-bold text-slate-100">
              Cloud Infrastructure Cost Estimator
            </CardTitle>
          </div>
          <span className="text-[10px] font-mono uppercase bg-slate-800 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
            Multi-Cloud Estimator
          </span>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Scale Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">Monthly Active Users (MAU)</label>
            <Input
              type="number"
              value={mau}
              onChange={(e) => setMau(Math.max(100, parseInt(e.target.value) || 0))}
              className="bg-slate-900 border-slate-800 text-slate-100 h-9 text-sm"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">API Requests / Mo</label>
            <Input
              type="number"
              value={reqs}
              onChange={(e) => setReqs(Math.max(1000, parseInt(e.target.value) || 0))}
              className="bg-slate-900 border-slate-800 text-slate-100 h-9 text-sm"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">Database Size (GB)</label>
            <Input
              type="number"
              value={dbGb}
              onChange={(e) => setDbGb(Math.max(1, parseInt(e.target.value) || 0))}
              className="bg-slate-900 border-slate-800 text-slate-100 h-9 text-sm"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">AI Tokens (Millions / Mo)</label>
            <Input
              type="number"
              value={tokensM}
              onChange={(e) => setTokensM(Math.max(0, parseInt(e.target.value) || 0))}
              className="bg-slate-900 border-slate-800 text-slate-100 h-9 text-sm"
            />
          </div>
        </div>

        {/* Multi-Provider Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="text-xs font-semibold text-slate-300">Vercel (Pro Edge)</div>
            <div className="text-xl font-bold text-slate-100 mt-1">${vercelCost}<span className="text-xs text-slate-500 font-normal">/mo</span></div>
            <div className="text-[10px] text-slate-500 mt-1">Zero-devops frontend hosting</div>
          </div>
          <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="text-xs font-semibold text-slate-300">Supabase (PostgreSQL)</div>
            <div className="text-xl font-bold text-slate-100 mt-1">${supaCost}<span className="text-xs text-slate-500 font-normal">/mo</span></div>
            <div className="text-[10px] text-slate-500 mt-1">Managed DB &amp; Connection Pooler</div>
          </div>
          <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="text-xs font-semibold text-slate-300">AI Inference Spend</div>
            <div className="text-xl font-bold text-indigo-400 mt-1">${aiCost}<span className="text-xs text-slate-500 font-normal">/mo</span></div>
            <div className="text-[10px] text-slate-500 mt-1">Blended Groq/Gemini tokens</div>
          </div>
          <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="text-xs font-semibold text-slate-300">AWS (ECS + RDS)</div>
            <div className="text-xl font-bold text-slate-400 mt-1">${awsCost}<span className="text-xs text-slate-500 font-normal">/mo</span></div>
            <div className="text-[10px] text-slate-500 mt-1">Full enterprise VPC topology</div>
          </div>
        </div>

        {/* Recommended Total Banner */}
        <div className="p-4 rounded-lg bg-indigo-950/20 border border-indigo-500/30 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Recommended Lean Modern Stack</div>
            <div className="text-sm text-slate-200 mt-0.5">Vercel + Supabase Managed PostgreSQL + AI Gateway</div>
          </div>
          <div className="text-2xl font-black text-indigo-300">
            ${recommendedTotal}<span className="text-xs text-slate-400 font-normal">/mo</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
