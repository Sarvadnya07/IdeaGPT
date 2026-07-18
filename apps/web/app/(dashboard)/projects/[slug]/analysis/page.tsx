"use client";

import React, { useState, useEffect, use } from "react";
import { useProjects } from "../../../../../hooks/useProjects";
import { useIdea, IdeaData } from "../../../../../hooks/useIdea";
import { useEvaluation } from "../../../../../hooks/useEvaluation";
import { useInsights } from "../../../../../hooks/useInsights";
import { BrainCircuit, Loader2, ArrowRight, CheckCircle2, ChevronRight, AlertTriangle, ChevronDown, Target, Users, Swords, Wrench, DollarSign, Shield, Lightbulb, History } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import Link from 'next/link';

function InsightModule({ title, icon: Icon, color, children }: { title: string; icon: React.ComponentType<any>; color: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="bg-[#0b0b0d] border border-zinc-800/60 rounded-2xl overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between p-5 hover:bg-zinc-900/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${color}`}>
            <Icon className="w-4 h-4" />
          </div>
          <span className="text-sm font-bold text-white">{title}</span>
        </div>
        <ChevronDown className={`w-4 h-4 text-zinc-500 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="px-5 pb-5 border-t border-zinc-800/60 pt-4 space-y-3 animate-in fade-in slide-in-from-top-2">
          {children}
        </div>
      )}
    </div>
  );
}

export default function AnalysisPage({ params }: { params: Promise<{ slug: string }> }) {
  const { projectsQuery } = useProjects();
  const { slug } = use(params);
  const project = projectsQuery.data?.items.find(p => p.slug === slug);

  const { ideasQuery, saveIdea } = useIdea(project?.id);
  const [jobId, setJobId] = useState<string | null>(null);
  const { triggerEvaluation, evaluationQuery } = useEvaluation(jobId);
  const insightsQuery = useInsights(evaluationQuery.data?.status === "COMPLETED" ? evaluationQuery.data?.id || null : null);
  const insights = insightsQuery.data;

  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<Partial<IdeaData>>({
    elevator_pitch: "",
    target_audience: "",
    core_problem: "",
    existing_tech_stack: "",
    primary_platforms: "Web",
    monetization_model: "",
    key_competitors: "",
    technical_risks: "",
  });

  const firstIdea = ideasQuery.data?.[0];

  // Pre-fill form if idea exists
  useEffect(() => {
    if (firstIdea) {
       setFormData(firstIdea);
    }
  }, [firstIdea]);

  if (projectsQuery.isLoading || ideasQuery.isLoading) {
    return <div className="py-20 flex justify-center"><Loader2 className="w-8 h-8 animate-spin text-indigo-500" /></div>;
  }

  if (!project) return <div className="text-red-400">Project Not Found.</div>;

  const handleNext = () => setStep(s => s + 1);
  const handlePrev = () => setStep(s => s - 1);

  const handleSubmit = async () => {
    try {
      // 1. Save Idea
      const savedIdea = await saveIdea.mutateAsync({ projectId: project.id, payload: formData });
      
      // 2. Trigger Evaluation
      const job = await triggerEvaluation.mutateAsync({ ideaId: savedIdea.id || firstIdea?.id || '' });
      
      // 3. Set Job ID to start polling
      setJobId(job.id);
    } catch (e) {
      console.error(e);
      alert("Failed to submit idea for evaluation.");
    }
  };

  const jobStatus = evaluationQuery.data?.status;

  // Render Polling / Results State
  if (jobId || jobStatus) {
    if (jobStatus === "PENDING" || jobStatus === "QUEUED" || jobStatus === "RUNNING" || !jobStatus) {
      return (
        <div className="flex flex-col items-center justify-center py-32 space-y-6">
          <div className="relative">
            <div className="absolute inset-0 bg-indigo-500 blur-xl opacity-20 animate-pulse rounded-full" />
            <BrainCircuit className="w-20 h-20 text-indigo-400 animate-bounce relative z-10" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">AI is Analyzing Your Idea</h2>
          <div className="flex items-center gap-2 text-zinc-400 text-sm">
            <Loader2 className="w-4 h-4 animate-spin" />
            {jobStatus === "QUEUED" ? "Waiting in queue..." : "Processing neural evaluation..."}
          </div>
          <div className="w-64 h-2 bg-zinc-900 rounded-full overflow-hidden border border-zinc-800">
             <div className="h-full bg-indigo-500 w-1/2 animate-[pulse_2s_ease-in-out_infinite]" />
          </div>
        </div>
      );
    }

    if (jobStatus === "COMPLETED" && evaluationQuery.data?.result_payload) {
      const result = evaluationQuery.data.result_payload;
      const metadata = result.metadata || {};

      const dimensions = result.dimensions || {
        innovation: 75,
        market_potential: 70,
        technical_feasibility: 65,
        business_viability: 70,
        scalability: 75,
        execution_complexity: 60,
        competitive_differentiation: 70
      };

      const keys = [
        { name: "Innovation", val: dimensions.innovation },
        { name: "Market", val: dimensions.market_potential },
        { name: "Execution", val: dimensions.execution_complexity },
        { name: "Technical", val: dimensions.technical_feasibility },
        { name: "Business", val: dimensions.business_viability },
        { name: "Scalability", val: dimensions.scalability },
        { name: "Investment", val: dimensions.competitive_differentiation }
      ];

      // Calculate coordinates for 300x300 SVG Radar Chart
      const cx = 150;
      const cy = 150;
      const r = 90;
      
      const gridCircles = [0.25, 0.5, 0.75, 1.0];
      const polygonPoints = keys.map((key, i) => {
        const angle = (i * 2 * Math.PI) / keys.length - Math.PI / 2;
        const x = cx + (key.val / 100) * r * Math.cos(angle);
        const y = cy + (key.val / 100) * r * Math.sin(angle);
        return `${x},${y}`;
      }).join(" ");

      const handleExport = async (format: "markdown" | "json") => {
        try {
          const res = await fetch(`http://localhost:8000/api/v1/exports/${format}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ evaluation_id: evaluationQuery.data?.id })
          });
          const data = await res.json();
          const blob = new Blob([data.content], { type: "text/plain" });
          const url = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = data.filename;
          link.click();
        } catch (err) {
          alert("Export failed.");
        }
      };

      return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div className="flex flex-col md:flex-row justify-between md:items-center bg-[#0b0b0d] border border-zinc-800 p-6 rounded-2xl gap-4">
             <div>
               <h2 className="text-2xl font-bold text-white mb-2">Evaluation Complete</h2>
               <p className="text-zinc-400 text-sm">Here is the architectural and strategic breakdown of your idea.</p>
             </div>
             <div className="flex items-center gap-4">
               <div className="w-20 h-20 rounded-full border-4 border-indigo-500 flex items-center justify-center bg-indigo-500/10">
                  <span className="text-2xl font-black text-indigo-400">{result.score || 85}</span>
               </div>
               <div className="flex flex-col gap-2">
                 <button onClick={() => handleExport("markdown")} className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white rounded-lg text-xs font-semibold transition-colors">
                   Download Markdown
                 </button>
                 <button onClick={() => handleExport("json")} className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white rounded-lg text-xs font-semibold transition-colors">
                   Download JSON
                 </button>
               </div>
             </div>
          </div>

          {/* Premium Radar Visualization & Category Scores */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-[#0b0b0d] border border-zinc-800/80 p-6 rounded-2xl flex flex-col items-center justify-center">
              <h3 className="text-sm font-bold text-zinc-400 mb-4 tracking-wider uppercase">Visual Score Dimensions</h3>
              <svg width="300" height="300" className="overflow-visible">
                {/* Outer/Inner Grid Circles */}
                {gridCircles.map((factor, idx) => (
                  <circle
                    key={idx}
                    cx={cx}
                    cy={cy}
                    r={r * factor}
                    fill="none"
                    stroke="#27272a"
                    strokeWidth="1"
                    strokeDasharray="4 4"
                  />
                ))}
                
                {/* Axis Lines & Labels */}
                {keys.map((key, i) => {
                  const angle = (i * 2 * Math.PI) / keys.length - Math.PI / 2;
                  const xGrid = cx + r * Math.cos(angle);
                  const yGrid = cy + r * Math.sin(angle);
                  const xLabel = cx + (r + 20) * Math.cos(angle);
                  const yLabel = cy + (r + 10) * Math.sin(angle);
                  return (
                    <g key={i}>
                      <line x1={cx} y1={cy} x2={xGrid} y2={yGrid} stroke="#27272a" strokeWidth="1" />
                      <text
                        x={xLabel}
                        y={yLabel}
                        fill="#a1a1aa"
                        fontSize="10"
                        fontWeight="600"
                        textAnchor="middle"
                        alignmentBaseline="middle"
                      >
                        {key.name}
                      </text>
                    </g>
                  );
                })}

                {/* Score Area Polygon */}
                <polygon
                  points={polygonPoints}
                  fill="rgba(99, 102, 241, 0.15)"
                  stroke="#6366f1"
                  strokeWidth="2"
                />
              </svg>
            </div>

            <div className="bg-[#0b0b0d] border border-zinc-800/80 p-6 rounded-2xl space-y-4">
              <h3 className="text-sm font-bold text-zinc-400 tracking-wider uppercase mb-2">Detailed Category Scores</h3>
              <div className="space-y-3">
                {keys.map((key, i) => (
                  <div key={i} className="space-y-1">
                    <div className="flex justify-between text-xs font-semibold text-zinc-300">
                      <span>{key.name}</span>
                      <span className="text-indigo-400">{key.val}/100</span>
                    </div>
                    <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden border border-zinc-800">
                      <div className="h-full bg-indigo-500" style={{ width: `${key.val}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-[#0b0b0d] border border-green-900/30 p-6 rounded-2xl">
              <h3 className="text-lg font-bold text-green-400 mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5" /> Key Strengths
              </h3>
              <ul className="space-y-2 text-zinc-300 text-sm">
                {(result.strengths || []).map((s: string, i: number) => <li key={i}>• {s}</li>)}
              </ul>
            </div>
            <div className="bg-[#0b0b0d] border border-red-900/30 p-6 rounded-2xl">
              <h3 className="text-lg font-bold text-red-400 mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" /> Potential Weaknesses
              </h3>
              <ul className="space-y-2 text-zinc-300 text-sm">
                {(result.weaknesses || []).map((w: string, i: number) => <li key={i}>• {w}</li>)}
              </ul>
            </div>
          </div>

          <div className="bg-[#0b0b0d] border border-zinc-800 p-6 rounded-2xl space-y-4">
             <h3 className="text-lg font-bold text-white">Technical Architecture Breakdown</h3>
             <div className="prose prose-invert max-w-none text-sm text-zinc-300">
               <ReactMarkdown>{result.architecture_breakdown || "No breakdown provided."}</ReactMarkdown>
             </div>
          </div>

          {/* Explainability & Debugging Metadata */}
          <div className="bg-[#0b0b0d]/60 border border-zinc-800/40 p-4 rounded-xl text-xs text-zinc-500 flex flex-wrap gap-x-8 gap-y-2">
            <div><strong>Provider:</strong> {metadata.provider || "N/A"}</div>
            <div><strong>Model:</strong> {metadata.model || "N/A"}</div>
            <div><strong>Prompt Version:</strong> {metadata.prompt_version || "1.0"}</div>
            <div><strong>Latency:</strong> {metadata.duration_ms ? `${metadata.duration_ms}ms` : "N/A"}</div>
            <div><strong>Cached:</strong> {metadata.cached ? "Yes" : "No"}</div>
          </div>

          {/* --- INSIGHTS MODULE DASHBOARD --- */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-white">Deep Analysis Modules</h3>
              <Link
                href={`/projects/${slug}/history`}
                className="flex items-center gap-1.5 text-xs font-bold text-zinc-500 hover:text-white transition-colors"
              >
                <History className="w-3.5 h-3.5" /> View History
              </Link>
            </div>

            {insightsQuery.isLoading && (
              <div className="flex justify-center py-8">
                <Loader2 className="w-6 h-6 text-indigo-500 animate-spin" />
              </div>
            )}

            {insights && (
              <>
                {/* SWOT */}
                <InsightModule title="SWOT Analysis" icon={Target} color="bg-indigo-500/10 text-indigo-400">
                  <div className="grid grid-cols-2 gap-3">
                    {(["strengths", "weaknesses", "opportunities", "threats"] as const).map((key) => (
                      <div key={key} className={`rounded-xl p-3.5 space-y-2 ${
                        key === "strengths" ? "bg-emerald-500/5 border border-emerald-500/15" :
                        key === "weaknesses" ? "bg-red-500/5 border border-red-500/15" :
                        key === "opportunities" ? "bg-indigo-500/5 border border-indigo-500/15" :
                        "bg-orange-500/5 border border-orange-500/15"
                      }`}>
                        <span className={`text-[9px] font-bold uppercase tracking-widest block ${
                          key === "strengths" ? "text-emerald-400" :
                          key === "weaknesses" ? "text-red-400" :
                          key === "opportunities" ? "text-indigo-400" :
                          "text-orange-400"
                        }`}>{key}</span>
                        <ul className="space-y-1">
                          {insights.swot[key].map((item, i) => (
                            <li key={i} className="text-[11px] text-zinc-400 leading-relaxed flex gap-1.5"><span className="text-zinc-600 mt-0.5">•</span>{item}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </InsightModule>

                {/* Market Analysis */}
                <InsightModule title="Market Analysis" icon={Users} color="bg-purple-500/10 text-purple-400">
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    {[
                      { label: "TAM", value: insights.market_analysis.tam },
                      { label: "SAM", value: insights.market_analysis.sam.split("—")[0] },
                      { label: "SOM", value: insights.market_analysis.som.split("—")[0] },
                    ].map(m => (
                      <div key={m.label} className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-3 text-center">
                        <div className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest mb-1">{m.label}</div>
                        <div className="text-sm font-black text-white">{m.value}</div>
                      </div>
                    ))}
                  </div>
                  <div className="text-[11px] text-zinc-400 space-y-1.5">
                    <div><span className="text-zinc-500 font-bold">Maturity:</span> {insights.market_analysis.market_maturity}</div>
                    <div><span className="text-zinc-500 font-bold">Barriers:</span> {insights.market_analysis.adoption_barriers.join(", ")}</div>
                  </div>
                </InsightModule>

                {/* Competitor Analysis */}
                <InsightModule title="Competitor Analysis" icon={Swords} color="bg-rose-500/10 text-rose-400">
                  <div className="space-y-3">
                    <div>
                      <div className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest mb-2">Competitive Advantages</div>
                      <div className="flex flex-wrap gap-2">
                        {insights.competitor_analysis.competitive_advantages.map((a, i) => (
                          <span key={i} className="text-[10px] bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full font-semibold">{a}</span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest mb-2">Competitive Gaps</div>
                      <div className="flex flex-wrap gap-2">
                        {insights.competitor_analysis.competitive_gaps.map((g, i) => (
                          <span key={i} className="text-[10px] bg-orange-500/10 border border-orange-500/20 text-orange-400 px-2 py-0.5 rounded-full font-semibold">{g}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </InsightModule>

                {/* Technical Feasibility */}
                <InsightModule title="Technical Feasibility" icon={Wrench} color="bg-sky-500/10 text-sky-400">
                  <div className="grid grid-cols-2 gap-4 text-[11px] text-zinc-400">
                    <div><span className="text-zinc-500 font-bold block mb-0.5">Complexity</span>{insights.technical_feasibility.engineering_complexity}</div>
                    <div><span className="text-zinc-500 font-bold block mb-0.5">Timeline</span>{insights.technical_feasibility.development_timeline}</div>
                    <div className="col-span-2"><span className="text-zinc-500 font-bold block mb-0.5">Infrastructure</span>{insights.technical_feasibility.infrastructure}</div>
                  </div>
                </InsightModule>

                {/* Business Model */}
                <InsightModule title="Business Model" icon={DollarSign} color="bg-emerald-500/10 text-emerald-400">
                  <div className="space-y-2 text-[11px] text-zinc-400">
                    <div><span className="text-zinc-500 font-bold">Revenue Model:</span> {insights.business_model.revenue_model}</div>
                    <div><span className="text-zinc-500 font-bold">Pricing:</span> {insights.business_model.pricing}</div>
                    <div><span className="text-zinc-500 font-bold">Acquisition:</span> {insights.business_model.customer_acquisition}</div>
                    <div className="flex gap-6 pt-1">
                      <div className="text-center">
                        <div className="text-xl font-black text-white">{insights.business_model.viability_score}</div>
                        <div className="text-[9px] text-zinc-500 uppercase tracking-widest">Viability</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-black text-white">{insights.business_model.scalability_score}</div>
                        <div className="text-[9px] text-zinc-500 uppercase tracking-widest">Scalability</div>
                      </div>
                    </div>
                  </div>
                </InsightModule>

                {/* Risk Analysis */}
                <InsightModule title="Risk Matrix" icon={Shield} color="bg-orange-500/10 text-orange-400">
                  <div className="space-y-3">
                    {Object.entries(insights.risk_analysis).map(([key, risk]) => (
                      <div key={key} className="flex items-start gap-3">
                        <span className={`text-[9px] font-bold px-2 py-0.5 rounded uppercase tracking-widest shrink-0 mt-0.5 ${
                          risk.level === "Low" || risk.level === "Low–Medium" ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400" :
                          risk.level === "Medium" ? "bg-orange-500/10 border border-orange-500/20 text-orange-400" :
                          "bg-red-500/10 border border-red-500/20 text-red-400"
                        }`}>{risk.level}</span>
                        <div>
                          <div className="text-[10px] font-bold text-white capitalize">{key.replace("_", " ")}</div>
                          <div className="text-[10px] text-zinc-500">{risk.description}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </InsightModule>

                {/* Recommendations */}
                <InsightModule title="AI Recommendations" icon={Lightbulb} color="bg-yellow-500/10 text-yellow-400">
                  <div className="space-y-4">
                    {(["quick_wins", "medium_term", "long_term"] as const).map((tier) => (
                      <div key={tier}>
                        <div className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest mb-2">
                          {tier === "quick_wins" ? "⚡ Quick Wins" : tier === "medium_term" ? "📈 Medium-Term" : "🚀 Long-Term"}
                        </div>
                        <div className="space-y-1.5">
                          {insights.recommendations[tier].map((rec, i) => (
                            <div key={i} className="flex gap-2 text-[11px] text-zinc-400">
                              <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                              {rec}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </InsightModule>
              </>
            )}
          </div>

          <div className="flex justify-end">
            <button onClick={() => setJobId(null)} className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg text-sm font-medium transition-colors">
              Rerun Analysis
            </button>
          </div>
        </div>
      );
    }


    if (jobStatus === "FAILED") {
      return <div className="text-red-500 p-6 bg-red-500/10 rounded-xl border border-red-500/20">Evaluation Failed. Please try again.</div>;
    }
  }

  // Render Form
  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2">Idea Submission Pipeline</h1>
        <p className="text-zinc-500 text-sm">Provide details about your startup to receive an AI-generated technical assessment.</p>
      </div>

      <div className="flex items-center gap-2 mb-8 bg-[#0b0b0d] p-4 rounded-xl border border-zinc-800/60 overflow-x-auto">
        {[1, 2, 3].map((s) => (
          <React.Fragment key={s}>
            <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold transition-colors ${step >= s ? 'bg-indigo-600 text-white' : 'bg-zinc-800 text-zinc-500'}`}>
              {s}
            </div>
            {s < 3 && <div className={`w-12 h-0.5 ${step > s ? 'bg-indigo-600' : 'bg-zinc-800'}`} />}
          </React.Fragment>
        ))}
      </div>

      <div className="bg-[#0b0b0d] border border-zinc-800/60 p-8 rounded-2xl shadow-xl">
        {step === 1 && (
          <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
            <h2 className="text-xl font-bold text-white mb-6">Core Concept</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-1">Elevator Pitch *</label>
                <textarea 
                  value={formData.elevator_pitch} 
                  onChange={e => setFormData({...formData, elevator_pitch: e.target.value})}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500 h-24 resize-none"
                  placeholder="Describe your idea in 2-3 sentences..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-1">Core Problem *</label>
                <textarea 
                  value={formData.core_problem} 
                  onChange={e => setFormData({...formData, core_problem: e.target.value})}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500 h-24 resize-none"
                  placeholder="What specific problem does this solve?"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-1">Target Audience *</label>
                <input 
                  value={formData.target_audience} 
                  onChange={e => setFormData({...formData, target_audience: e.target.value})}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500"
                  placeholder="e.g. Remote software engineers"
                />
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
            <h2 className="text-xl font-bold text-white mb-6">Technical Details</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-1">Primary Platforms</label>
                <select 
                  value={formData.primary_platforms} 
                  onChange={e => setFormData({...formData, primary_platforms: e.target.value})}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="Web App">Web App</option>
                  <option value="Mobile App (iOS/Android)">Mobile App (iOS/Android)</option>
                  <option value="Desktop">Desktop</option>
                  <option value="API / SaaS">API / SaaS</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-1">Existing Tech Stack / Preferences</label>
                <input 
                  value={formData.existing_tech_stack} 
                  onChange={e => setFormData({...formData, existing_tech_stack: e.target.value})}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500"
                  placeholder="e.g. Prefer Next.js and Python"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-1">Monetization Model</label>
                <input 
                  value={formData.monetization_model} 
                  onChange={e => setFormData({...formData, monetization_model: e.target.value})}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500"
                  placeholder="e.g. B2B Subscription, Freemium"
                />
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
            <h2 className="text-xl font-bold text-white mb-6">Competitors & Risks</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-1">Key Competitors</label>
                <textarea 
                  value={formData.key_competitors} 
                  onChange={e => setFormData({...formData, key_competitors: e.target.value})}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500 h-24 resize-none"
                  placeholder="Who else is doing this?"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-1">Perceived Technical Risks</label>
                <textarea 
                  value={formData.technical_risks} 
                  onChange={e => setFormData({...formData, technical_risks: e.target.value})}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500 h-24 resize-none"
                  placeholder="e.g. High latency in AI processing, data privacy"
                />
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-between mt-10 pt-6 border-t border-zinc-800/60">
          <button 
            onClick={handlePrev} 
            disabled={step === 1}
            className="px-6 py-2.5 rounded-lg text-sm font-medium text-zinc-400 hover:text-white disabled:opacity-30 transition-colors"
          >
            Back
          </button>
          
          {step < 3 ? (
            <button 
              onClick={handleNext} 
              disabled={step === 1 && (!formData.elevator_pitch || !formData.core_problem || !formData.target_audience)}
              className="flex items-center gap-2 px-6 py-2.5 bg-zinc-100 hover:bg-white text-zinc-900 rounded-lg text-sm font-bold disabled:opacity-50 transition-colors"
            >
              Next Step <ChevronRight className="w-4 h-4" />
            </button>
          ) : (
            <button 
              onClick={handleSubmit} 
              disabled={saveIdea.isPending || triggerEvaluation.isPending}
              className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-bold shadow-[0_0_20px_rgba(79,70,229,0.4)] transition-all"
            >
              {(saveIdea.isPending || triggerEvaluation.isPending) ? <Loader2 className="w-4 h-4 animate-spin" /> : <BrainCircuit className="w-4 h-4" />}
              Analyze Idea
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
