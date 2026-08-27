"use client";

import React, { useState } from "react";
import { useProjects } from "../../../hooks/useProjects";
import { useApiClient } from "@/lib/api/client";
import { toast } from "sonner";
import {
  GraduationCap,
  Sparkles,
  Compass,
  AlertOctagon,
  Calendar,
  HelpCircle,
  Loader2,
  RefreshCw,
  UserCheck,
} from "lucide-react";

interface MentorPersona {
  name: string;
  role: string;
  philosophy: string;
}

interface BlindspotItem {
  blindspot: string;
  why_it_kills_startups: string;
  immediate_action: string;
}

interface MentalModelItem {
  model_name: string;
  how_to_apply: string;
}

interface ExecutionPlan {
  days_30: string[];
  days_60: string[];
  days_90: string[];
}

interface MentorLabResult {
  mentor_persona: MentorPersona;
  executive_coaching_summary: string;
  top_founder_blindspots: BlindspotItem[];
  applied_mental_models: MentalModelItem[];
  execution_plan_30_60_90: ExecutionPlan;
  critical_questions_for_the_founder: string[];
}

export default function MentorLabPage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects();
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const activeProjectId = selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<MentorLabResult | null>(null);

  const handleGenerate = async () => {
    if (!activeProject) {
      toast.error("Please select a project first.");
      return;
    }
    setIsGenerating(true);
    try {
      const res = await api.post<MentorLabResult>("/ai/labs/mentor", {
        title: activeProject.title,
        category: activeProject.category || "B2B SaaS",
        stage: "Early Stage / Seed",
        challenges: "Customer acquisition velocity and architectural scaling",
      });
      setResult(res.data);
      toast.success("Founder Mentoring Session synthesized successfully!");
    } catch (err: any) {
      toast.error("Failed to generate mentoring session");
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
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 uppercase tracking-widest gap-1.5">
              <GraduationCap className="w-3 h-3" /> Founder Mentorship Lab
            </span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            {activeProject?.title || "Executive Founder Advisory"}
          </h1>
          <p className="text-xs text-zinc-500 max-w-2xl leading-relaxed">
            High-leverage executive coaching, founder blindspot diagnostics, applied decision mental models,
            and structured 30-60-90 day execution milestones.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3 shrink-0">
          <select
            value={activeProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="bg-[#0b0b0d] border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
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
            className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] cursor-pointer"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> Consulting Mentor...
              </>
            ) : (
              <>
                <RefreshCw className="w-3.5 h-3.5" /> Start Advisory Session
              </>
            )}
          </button>
        </div>
      </div>

      {result ? (
        <div className="space-y-6">
          {/* Mentor Persona & Executive Advice */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-950/30 to-purple-950/30 border border-indigo-900/40 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <UserCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">{result.mentor_persona.name}</h3>
                <span className="text-xs text-indigo-300 block">{result.mentor_persona.role}</span>
              </div>
            </div>
            <p className="text-xs text-zinc-300 leading-relaxed font-medium">
              &ldquo;{result.executive_coaching_summary}&rdquo;
            </p>
            <span className="text-[11px] text-zinc-500 font-mono block pt-2 border-t border-indigo-950/60">
              Core Mantra: {result.mentor_persona.philosophy}
            </span>
          </div>

          {/* Top Founder Blindspots */}
          <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
            <div className="flex items-center gap-2">
              <AlertOctagon className="w-4 h-4 text-red-400" />
              <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">Top Founder Blindspots & Traps</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {result.top_founder_blindspots.map((b, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-black/40 border border-zinc-900 space-y-2">
                  <span className="text-xs font-bold text-red-400 block">{b.blindspot}</span>
                  <p className="text-[11px] text-zinc-400 leading-relaxed">{b.why_it_kills_startups}</p>
                  <div className="pt-2 border-t border-zinc-900">
                    <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block">Immediate Action:</span>
                    <span className="text-[11px] text-zinc-300">{b.immediate_action}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Applied Mental Models & 30-60-90 Day Plan */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Mental Models */}
            <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
              <div className="flex items-center gap-2">
                <Compass className="w-4 h-4 text-amber-400" />
                <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">Applied Mental Models</h3>
              </div>
              <div className="space-y-3">
                {result.applied_mental_models.map((m, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-black/40 border border-zinc-900 space-y-1">
                    <span className="text-xs font-bold text-amber-400 block">{m.model_name}</span>
                    <p className="text-[11px] text-zinc-300 leading-relaxed">{m.how_to_apply}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* 30-60-90 Execution Plan */}
            <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">30-60-90 Day Action Plan</h3>
              </div>
              <div className="space-y-3 text-xs">
                <div className="p-3 rounded-xl bg-black/40 border border-zinc-900 space-y-1.5">
                  <span className="font-bold text-emerald-400 text-[11px] uppercase tracking-wider">First 30 Days (Customer Discovery & MVP)</span>
                  <ul className="text-[11px] text-zinc-400 list-disc list-inside space-y-1">
                    {result.execution_plan_30_60_90.days_30.map((task, i) => (
                      <li key={i}>{task}</li>
                    ))}
                  </ul>
                </div>
                <div className="p-3 rounded-xl bg-black/40 border border-zinc-900 space-y-1.5">
                  <span className="font-bold text-indigo-400 text-[11px] uppercase tracking-wider">Days 31-60 (Retention & Product Loop)</span>
                  <ul className="text-[11px] text-zinc-400 list-disc list-inside space-y-1">
                    {result.execution_plan_30_60_90.days_60.map((task, i) => (
                      <li key={i}>{task}</li>
                    ))}
                  </ul>
                </div>
                <div className="p-3 rounded-xl bg-black/40 border border-zinc-900 space-y-1.5">
                  <span className="font-bold text-purple-400 text-[11px] uppercase tracking-wider">Days 61-90 (Monetization & Sales Velocity)</span>
                  <ul className="text-[11px] text-zinc-400 list-disc list-inside space-y-1">
                    {result.execution_plan_30_60_90.days_90.map((task, i) => (
                      <li key={i}>{task}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Hard Questions for the Founder */}
          <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
            <div className="flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-purple-400" />
              <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">Critical Strategic Questions for Founders</h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {result.critical_questions_for_the_founder.map((q, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-black/40 border border-zinc-900 text-xs text-zinc-300 flex items-start gap-2.5">
                  <span className="text-purple-400 font-bold font-mono">Q{idx + 1}.</span>
                  <span className="leading-relaxed">{q}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20 border border-zinc-900/60 rounded-2xl bg-[#0b0b0d] text-center p-8 space-y-4">
          <GraduationCap className="w-12 h-12 text-zinc-700 mb-2" />
          <h3 className="text-lg font-bold text-white">No Mentoring Session Recorded</h3>
          <p className="text-xs text-zinc-500 max-w-md leading-relaxed">
            Click &quot;Start Advisory Session&quot; to diagnose early-stage blindspots and formulate an actionable 90-day plan.
          </p>
        </div>
      )}
    </div>
  );
}
