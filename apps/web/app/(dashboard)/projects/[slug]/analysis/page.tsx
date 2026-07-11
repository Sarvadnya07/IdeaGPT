"use client";

import React, { useState, useEffect } from "react";
import { useProjects } from "../../../../../hooks/useProjects";
import { useIdea, IdeaData } from "../../../../../hooks/useIdea";
import { useEvaluation } from "../../../../../hooks/useEvaluation";
import { BrainCircuit, Loader2, ArrowRight, CheckCircle2, ChevronRight, AlertTriangle } from "lucide-react";
import ReactMarkdown from 'react-markdown';

export default function AnalysisPage({ params }: { params: { slug: string } }) {
  const { projectsQuery } = useProjects();
  const project = projectsQuery.data?.items.find(p => p.slug === params.slug);

  const { ideaQuery, saveIdea } = useIdea(project?.id);
  const [jobId, setJobId] = useState<number | null>(null);
  const { triggerEvaluation, evaluationQuery } = useEvaluation(jobId);

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

  // Pre-fill form if idea exists
  useEffect(() => {
    if (ideaQuery.data && !ideaQuery.data.project_id) {
       // empty object fallback in backend returns just project_id if not found sometimes, but let's be careful
       if (ideaQuery.data.elevator_pitch) {
         setFormData(ideaQuery.data);
       }
    }
  }, [ideaQuery.data]);

  if (projectsQuery.isLoading || ideaQuery.isLoading) {
    return <div className="py-20 flex justify-center"><Loader2 className="w-8 h-8 animate-spin text-indigo-500" /></div>;
  }

  if (!project) return <div className="text-red-400">Project Not Found.</div>;

  const handleNext = () => setStep(s => s + 1);
  const handlePrev = () => setStep(s => s - 1);

  const handleSubmit = async () => {
    try {
      // 1. Save Idea
      await saveIdea.mutateAsync({ projectId: project.id, payload: formData });
      
      // 2. Trigger Evaluation
      const job = await triggerEvaluation.mutateAsync(project.id);
      
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
    if (jobStatus === "QUEUED" || jobStatus === "PROCESSING" || !jobStatus) {
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
      return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div className="flex justify-between items-center bg-[#0b0b0d] border border-zinc-800 p-6 rounded-2xl">
             <div>
               <h2 className="text-2xl font-bold text-white mb-2">Evaluation Complete</h2>
               <p className="text-zinc-400">Here is the architectural and strategic breakdown of your idea.</p>
             </div>
             <div className="w-20 h-20 rounded-full border-4 border-indigo-500 flex items-center justify-center bg-indigo-500/10">
                <span className="text-2xl font-black text-indigo-400">{result.score || 85}</span>
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
            {s < 3 && <div className={`w-12 h-[2px] ${step > s ? 'bg-indigo-600' : 'bg-zinc-800'}`} />}
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
