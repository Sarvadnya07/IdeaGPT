"use client";

import React from "react";
import { Gauge, Zap, DollarSign, Activity, HelpCircle } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export interface AIUsageGaugeData {
  total_requests: number;
  total_tokens_consumed: number;
  estimated_cost_usd: number;
  fallback_executions_count: number;
  requests_by_provider: Record<string, number>;
  provider_quota_status: {
    groq: string;
    gemini: string;
    openai: string;
    ollama: string;
    external_remaining_quota: string;
  };
}

interface AICreditTokenGaugeProps {
  data?: AIUsageGaugeData;
}

export const AICreditTokenGauge: React.FC<AICreditTokenGaugeProps> = ({
  data = {
    total_requests: 48,
    total_tokens_consumed: 142850,
    estimated_cost_usd: 0.0857,
    fallback_executions_count: 2,
    requests_by_provider: {
      groq: 38,
      gemini: 8,
      openai: 2
    },
    provider_quota_status: {
      groq: "ACTIVE_UNMETERED",
      gemini: "ACTIVE_FREE_TIER",
      openai: "BYOK_CONFIGURED",
      ollama: "LOCAL_UNLIMITED",
      external_remaining_quota: "UNKNOWN"
    }
  }
}) => {
  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-4 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Gauge className="h-5 w-5 text-indigo-400" />
            <CardTitle className="text-base font-bold text-slate-100">
              AI Credit &amp; Token Gauge
            </CardTitle>
          </div>
          <span className="text-[10px] font-mono uppercase bg-slate-800 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
            Real Usage Telemetry
          </span>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Metric Counters Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold text-slate-400">Total Tokens</div>
            <div className="text-2xl font-black text-indigo-400">
              {data.total_tokens_consumed.toLocaleString()}
            </div>
            <div className="text-[10px] text-slate-500">Inbound + Outbound</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold text-slate-400">Total Requests</div>
            <div className="text-2xl font-black text-slate-100">
              {data.total_requests.toLocaleString()}
            </div>
            <div className="text-[10px] text-slate-500">Gateway Invocations</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold text-slate-400">Estimated Cost</div>
            <div className="text-2xl font-black text-emerald-400">
              ${data.estimated_cost_usd.toFixed(4)}
            </div>
            <div className="text-[10px] text-slate-500">Real Token FinOps</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold text-slate-400">Remaining Quota</div>
            <div className="text-xl font-bold text-slate-400 flex items-center gap-1">
              <span>{data.provider_quota_status.external_remaining_quota}</span>
              <span title="Unexposed upstream tier"><HelpCircle className="h-3.5 w-3.5 text-slate-500" /></span>
            </div>
            <div className="text-[10px] text-slate-500">External Provider Limit</div>
          </div>
        </div>

        {/* Provider Breakdown Badges */}
        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Invocations by AI Provider
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(data.requests_by_provider).map(([prov, count]) => (
              <div
                key={prov}
                className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 flex items-center gap-2 text-xs font-medium text-slate-300"
              >
                <span className="capitalize">{prov}:</span>
                <span className="font-mono font-bold text-indigo-400">{count} reqs</span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
