"use client";

import React, { useState } from "react";
import { useProjects } from "../../../hooks/useProjects";
import { useApiClient } from "@/lib/api/client";
import { toast } from "sonner";
import {
  Users,
  Briefcase,
  UserCheck,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  RefreshCw,
  Copy,
  Check,
  Award,
} from "lucide-react";

interface CompensationRange {
  salary_usd: string;
  equity_pct: string;
}

interface JobDescription {
  role_title: string;
  level: string;
  mission: string;
  responsibilities: string[];
  required_skills: string[];
  compensation_range: CompensationRange;
}

interface HiringPhase {
  phase: string;
  headcount: number;
  roles: string[];
  key_milestone_trigger: string;
}

interface InterviewScorecard {
  cultural_values: string[];
  technical_evaluation_probes: string[];
  red_flags_to_reject: string[];
}

interface RecruiterLabResult {
  hiring_roadmap: HiringPhase[];
  job_descriptions: JobDescription[];
  interview_scorecard: InterviewScorecard;
  talent_acquisition_strategy: string;
}

export default function RecruiterLabPage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects();
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const activeProjectId =
    selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<RecruiterLabResult | null>(null);
  const [selectedJobIdx, setSelectedJobIdx] = useState<number>(0);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!activeProject) {
      toast.error("Please select a project first.");
      return;
    }
    setIsGenerating(true);
    try {
      const res = await api.post<RecruiterLabResult>("/ai/labs/recruiter", {
        title: activeProject.title,
        category: activeProject.category || "B2B SaaS",
        current_team_size: "Founding Team (1-2)",
        target_roles:
          "Founding Full-Stack Engineer, Head of Growth, Product Designer",
      });
      setResult(res.data);
      toast.success("Executive Talent Blueprint synthesized successfully!");
    } catch (err: any) {
      toast.error("Failed to generate recruiting plan");
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    toast.success("Copied to clipboard!");
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const currentJob = result?.job_descriptions?.[selectedJobIdx] || null;

  return (
    <div className="space-y-8 py-4 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-zinc-900 pb-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-widest gap-1.5">
              <Users className="w-3 h-3" /> Talent & Recruiter Lab
            </span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            {activeProject?.title || "Hiring & Talent Architecture"}
          </h1>
          <p className="text-xs text-zinc-500 max-w-2xl leading-relaxed">
            Synthesize organizational hiring roadmaps, production job
            specifications, compensation & equity benchmarks, and candidate
            interview scorecards.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3 shrink-0">
          <select
            value={activeProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="bg-[#0b0b0d] border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500"
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
            className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)] cursor-pointer"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> Formulating
                Roles...
              </>
            ) : (
              <>
                <RefreshCw className="w-3.5 h-3.5" /> Plan Hiring Blueprint
              </>
            )}
          </button>
        </div>
      </div>

      {result ? (
        <div className="space-y-6">
          {/* Sourcing Strategy Banner */}
          <div className="p-6 rounded-2xl bg-emerald-950/20 border border-emerald-900/40">
            <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-400 block mb-2">
              Founding Talent Acquisition Strategy
            </span>
            <p className="text-xs text-zinc-300 leading-relaxed">
              {result.talent_acquisition_strategy}
            </p>
          </div>

          {/* Hiring Roadmap Phases */}
          <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
            <div className="flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-emerald-400" />
              <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">
                Hiring Roadmap & Headcount
              </h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.hiring_roadmap.map((phase, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-black/40 border border-zinc-900 space-y-2"
                >
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-white">{phase.phase}</span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400">
                      +{phase.headcount} Hires
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {phase.roles.map((r, rIdx) => (
                      <span
                        key={rIdx}
                        className="px-2 py-0.5 bg-zinc-900 text-zinc-300 text-[10px] rounded-md font-mono"
                      >
                        {r}
                      </span>
                    ))}
                  </div>
                  <span className="text-[11px] text-zinc-500 block pt-1">
                    Trigger: {phase.key_milestone_trigger}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Job Descriptions Browser */}
          <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-indigo-400" />
                <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">
                  Role Specifications & JDs
                </h3>
              </div>
              <div className="flex gap-2">
                {result.job_descriptions.map((jd, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedJobIdx(idx)}
                    className={`px-3 py-1.5 text-xs font-medium rounded-xl transition-all ${
                      selectedJobIdx === idx
                        ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                        : "bg-zinc-900 text-zinc-400 hover:text-white"
                    }`}
                  >
                    {jd.role_title}
                  </button>
                ))}
              </div>
            </div>

            {currentJob && (
              <div className="p-5 rounded-xl bg-black/40 border border-zinc-900 space-y-4 text-xs">
                <div className="flex flex-wrap justify-between items-start gap-4">
                  <div>
                    <h4 className="text-sm font-bold text-white">
                      {currentJob.role_title}
                    </h4>
                    <span className="text-[11px] text-indigo-400 font-mono">
                      {currentJob.level} Level
                    </span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-zinc-900/80 border border-zinc-800 text-right">
                    <span className="text-white font-bold block">
                      {currentJob.compensation_range.salary_usd}
                    </span>
                    <span className="text-[10px] text-emerald-400 font-mono">
                      {currentJob.compensation_range.equity_pct} Equity
                    </span>
                  </div>
                </div>

                <div>
                  <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider block mb-1">
                    Mission
                  </span>
                  <p className="text-zinc-300 text-[11px] leading-relaxed">
                    {currentJob.mission}
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-zinc-900">
                  <div>
                    <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider block mb-1.5">
                      Core Responsibilities
                    </span>
                    <ul className="text-[11px] text-zinc-400 list-disc list-inside space-y-1">
                      {currentJob.responsibilities.map((res, i) => (
                        <li key={i}>{res}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider block mb-1.5">
                      Required Skills
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {currentJob.required_skills.map((skill, i) => (
                        <span
                          key={i}
                          className="px-2.5 py-1 bg-zinc-900 border border-zinc-800 text-zinc-300 text-[10px] rounded-lg"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Interview Scorecards */}
          <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 space-y-4">
            <div className="flex items-center gap-2">
              <Award className="w-4 h-4 text-purple-400" />
              <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider">
                Interview Rubrics & Evaluation
              </h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-black/40 border border-zinc-900 space-y-2">
                <span className="font-bold text-indigo-400 text-[11px] uppercase tracking-wider flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Cultural Values
                </span>
                <ul className="text-[11px] text-zinc-400 list-disc list-inside space-y-1">
                  {result.interview_scorecard.cultural_values.map((v, i) => (
                    <li key={i}>{v}</li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-black/40 border border-zinc-900 space-y-2">
                <span className="font-bold text-emerald-400 text-[11px] uppercase tracking-wider flex items-center gap-1.5">
                  <UserCheck className="w-3.5 h-3.5" /> Technical Probes
                </span>
                <ul className="text-[11px] text-zinc-400 list-disc list-inside space-y-1">
                  {result.interview_scorecard.technical_evaluation_probes.map(
                    (p, i) => (
                      <li key={i}>{p}</li>
                    ),
                  )}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-black/40 border border-zinc-900 space-y-2">
                <span className="font-bold text-red-400 text-[11px] uppercase tracking-wider flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5" /> Red Flags
                </span>
                <ul className="text-[11px] text-zinc-400 list-disc list-inside space-y-1">
                  {result.interview_scorecard.red_flags_to_reject.map(
                    (f, i) => (
                      <li key={i}>{f}</li>
                    ),
                  )}
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20 border border-zinc-900/60 rounded-2xl bg-[#0b0b0d] text-center p-8 space-y-4">
          <Users className="w-12 h-12 text-zinc-700 mb-2" />
          <h3 className="text-lg font-bold text-white">
            No Talent Blueprint Generated
          </h3>
          <p className="text-xs text-zinc-500 max-w-md leading-relaxed">
            Click &quot;Plan Hiring Blueprint&quot; to synthesize headcounts,
            compensation bands, job descriptions, and interview rubrics.
          </p>
        </div>
      )}
    </div>
  );
}
