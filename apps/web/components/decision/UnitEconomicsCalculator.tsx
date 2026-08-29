"use client";

import React, { useState } from "react";
import { Calculator, TrendingUp, DollarSign, Clock, ShieldCheck, AlertTriangle } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export const UnitEconomicsCalculator: React.FC = () => {
  const [price, setPrice] = useState<number>(29.0);
  const [cogs, setCogs] = useState<number>(4.0);
  const [cac, setCac] = useState<number>(45.0);
  const [churn, setChurn] = useState<number>(5.0);
  const [burn, setBurn] = useState<number>(5000.0);
  const [capital, setCapital] = useState<number>(50000.0);

  // Deterministic math calculations
  const grossMarginPct = price > 0 ? (((price - cogs) / price) * 100).toFixed(1) : "0.0";
  const lifetimeMonths = churn > 0 ? (1 / (churn / 100)).toFixed(1) : "999";
  const ltv = (parseFloat(lifetimeMonths) * (price - cogs)).toFixed(2);
  const ltvCac = cac > 0 ? (parseFloat(ltv) / cac).toFixed(1) : "0.0";
  const paybackMonths = price - cogs > 0 ? (cac / (price - cogs)).toFixed(1) : "999";
  const breakEvenCustomers = price - cogs > 0 ? Math.ceil(burn / (price - cogs)) : 999999;
  const runwayMonths = burn > 0 ? (capital / burn).toFixed(1) : "99";

  const isViable = parseFloat(ltvCac) >= 3.0 && parseFloat(paybackMonths) <= 12;

  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-4 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calculator className="h-5 w-5 text-indigo-400" />
            <CardTitle className="text-base font-bold text-slate-100">
              Unit Economics & Cash Flow Calculator
            </CardTitle>
          </div>
          <span className="text-[10px] font-mono uppercase bg-slate-800 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
            Deterministic Engine
          </span>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Input Parameters Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">Monthly Price / ARPU ($)</label>
            <Input
              type="number"
              value={price}
              onChange={(e) => setPrice(Math.max(1, parseFloat(e.target.value) || 0))}
              className="bg-slate-900 border-slate-800 text-slate-100 h-9 text-sm"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">Monthly COGS per User ($)</label>
            <Input
              type="number"
              value={cogs}
              onChange={(e) => setCogs(Math.max(0, parseFloat(e.target.value) || 0))}
              className="bg-slate-900 border-slate-800 text-slate-100 h-9 text-sm"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">Customer Acquisition Cost ($)</label>
            <Input
              type="number"
              value={cac}
              onChange={(e) => setCac(Math.max(1, parseFloat(e.target.value) || 0))}
              className="bg-slate-900 border-slate-800 text-slate-100 h-9 text-sm"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">Monthly Churn Rate (%)</label>
            <Input
              type="number"
              value={churn}
              onChange={(e) => setChurn(Math.max(0.5, parseFloat(e.target.value) || 0))}
              className="bg-slate-900 border-slate-800 text-slate-100 h-9 text-sm"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">Monthly Fixed Burn ($)</label>
            <Input
              type="number"
              value={burn}
              onChange={(e) => setBurn(Math.max(500, parseFloat(e.target.value) || 0))}
              className="bg-slate-900 border-slate-800 text-slate-100 h-9 text-sm"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">Available Capital ($)</label>
            <Input
              type="number"
              value={capital}
              onChange={(e) => setCapital(Math.max(0, parseFloat(e.target.value) || 0))}
              className="bg-slate-900 border-slate-800 text-slate-100 h-9 text-sm"
            />
          </div>
        </div>

        {/* Output Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="text-[11px] text-slate-400 font-medium">Gross Margin</div>
            <div className="text-xl font-black text-emerald-400 mt-1">{grossMarginPct}%</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Contribution per user</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="text-[11px] text-slate-400 font-medium">LTV / CAC Ratio</div>
            <div className={`text-xl font-black mt-1 ${parseFloat(ltvCac) >= 3.0 ? "text-emerald-400" : "text-amber-400"}`}>
              {ltvCac}x
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Target &gt;= 3.0x</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="text-[11px] text-slate-400 font-medium">CAC Payback</div>
            <div className="text-xl font-black text-indigo-400 mt-1">{paybackMonths} mo</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Recoup duration</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="text-[11px] text-slate-400 font-medium">Zero-Revenue Runway</div>
            <div className="text-xl font-black text-amber-400 mt-1">{runwayMonths} mo</div>
            <div className="text-[10px] text-slate-500 mt-0.5">At current burn</div>
          </div>
        </div>

        {/* Viability Status Banner */}
        <div className={`p-4 rounded-lg flex items-center justify-between border ${
          isViable ? "bg-emerald-950/20 border-emerald-500/30 text-emerald-300" : "bg-amber-950/20 border-amber-500/30 text-amber-300"
        }`}>
          <div className="flex items-center gap-3">
            {isViable ? <ShieldCheck className="h-5 w-5 text-emerald-400" /> : <AlertTriangle className="h-5 w-5 text-amber-400" />}
            <div>
              <div className="text-sm font-bold">{isViable ? "Venture-Scalable Unit Economics" : "Marginal / Fragile Economics"}</div>
              <div className="text-xs opacity-80 mt-0.5">
                Break-even requires {breakEvenCustomers.toLocaleString()} active paying subscribers.
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
