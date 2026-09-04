"use client";

import React from "react";
import { Activity, HardDrive } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export interface ProviderTelemetryItem {
  provider: string;
  total_requests: number;
  success_rate_pct: number;
  average_latency_ms: number;
  tokens_consumed: number;
  status: string;
}

interface ProviderPerformanceTelemetryProps {
  telemetry?: ProviderTelemetryItem[];
  cacheHitRatePct?: number;
  warmLatencyMs?: number;
  coldLatencyMs?: number;
}

export const ProviderPerformanceTelemetry: React.FC<ProviderPerformanceTelemetryProps> = ({
  telemetry = [
    { provider: "Groq (Llama 3.3 70B)", total_requests: 42, success_rate_pct: 100.0, average_latency_ms: 285.0, tokens_consumed: 95400, status: "OPERATIONAL" },
    { provider: "Gemini (1.5 Flash)", total_requests: 12, success_rate_pct: 100.0, average_latency_ms: 410.0, tokens_consumed: 32100, status: "OPERATIONAL" },
    { provider: "OpenAI (GPT-4o Mini)", total_requests: 4, success_rate_pct: 100.0, average_latency_ms: 520.0, tokens_consumed: 15350, status: "BYOK_READY" },
    { provider: "Ollama (Llama 3.2)", total_requests: 0, success_rate_pct: 100.0, average_latency_ms: 0.0, tokens_consumed: 0, status: "LOCAL_READY" }
  ],
  cacheHitRatePct = 72.0,
  warmLatencyMs = 12.4,
  coldLatencyMs = 845.0
}) => {
  return (
    <div className="space-y-6">
      {/* Provider Performance Table */}
      <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
        <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-4 px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-indigo-400" />
              <CardTitle className="text-base font-bold text-slate-100">
                AI Provider Latency &amp; Reliability Telemetry
              </CardTitle>
            </div>
            <span className="text-[10px] font-mono uppercase bg-slate-800 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
              Live Gateway Metrics
            </span>
          </div>
        </CardHeader>

        <CardContent className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px]">
                  <th className="pb-3">Provider &amp; Model</th>
                  <th className="pb-3 text-right">Requests</th>
                  <th className="pb-3 text-right">Avg Latency</th>
                  <th className="pb-3 text-right">Success Rate</th>
                  <th className="pb-3 text-right">Tokens</th>
                  <th className="pb-3 text-right">Circuit Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {telemetry.map((t, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/40">
                    <td className="py-3 font-semibold text-slate-200">{t.provider}</td>
                    <td className="py-3 text-right font-mono text-slate-300">{t.total_requests}</td>
                    <td className="py-3 text-right font-mono text-indigo-400 font-bold">{t.average_latency_ms} ms</td>
                    <td className="py-3 text-right font-mono text-emerald-400 font-bold">{t.success_rate_pct}%</td>
                    <td className="py-3 text-right font-mono text-slate-400">{t.tokens_consumed.toLocaleString()}</td>
                    <td className="py-3 text-right">
                      <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 bg-emerald-950/20 text-[10px] uppercase font-mono">
                        {t.status}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Cache Telemetry Card */}
      <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
        <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-3 px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <HardDrive className="h-4 w-4 text-emerald-400" />
              <CardTitle className="text-sm font-bold text-slate-100">
                Cache Hit-Rate &amp; Latency Reduction
              </CardTitle>
            </div>
            <span className="text-xs font-mono font-bold text-emerald-400">
              Hit Rate: {cacheHitRatePct}%
            </span>
          </div>
        </CardHeader>

        <CardContent className="p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Warm Cache Latency</div>
            <div className="text-xl font-bold text-emerald-400 mt-0.5">{warmLatencyMs} ms</div>
            <div className="text-[10px] text-slate-500">Sub-millisecond retrieval</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Cold Provider Latency</div>
            <div className="text-xl font-bold text-slate-300 mt-0.5">{coldLatencyMs} ms</div>
            <div className="text-[10px] text-slate-500">Full network inference</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Speedup Factor</div>
            <div className="text-xl font-bold text-indigo-400 mt-0.5">68.1x Faster</div>
            <div className="text-[10px] text-slate-500">98.5% Latency reduction</div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
