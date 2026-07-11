"use client";

import React, { useEffect, useState, useCallback, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useProjects } from "../../../../../hooks/useProjects";
import { useIdeaSubmission, IdeaData } from "../../../../../hooks/useIdeaSubmission";
import { Loader2, Save, Send, ChevronLeft } from "lucide-react";
import Link from "next/link";

function useDebounceCallback<T extends (...args: any[]) => void>(callback: T, delay: number) {
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  
  return useCallback((...args: Parameters<T>) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  }, [callback, delay]);
}

export default function IdeaSubmissionPage() {
  const { slug } = useParams();
  const router = useRouter();
  
  const { projectsQuery } = useProjects();
  const projects = projectsQuery.data?.items || [];
  const currentProject = projects.find(p => p.slug === slug);
  const projectId = currentProject?.id || null;

  const { ideaQuery, saveIdeaMutation, triggerEvaluationMutation } = useIdeaSubmission(projectId);

  const [formData, setFormData] = useState<IdeaData>({
    problem_statement: "",
    solution_description: "",
    target_audience: "",
    business_model: "",
    competitors: "",
    unique_selling_proposition: "",
    technology_stack: "",
    budget: "",
    timeline: "",
    additional_notes: "",
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  // Populate initial data
  useEffect(() => {
    if (ideaQuery.data) {
      setFormData(prev => ({ ...prev, ...ideaQuery.data }));
    }
  }, [ideaQuery.data]);

  const doSave = useCallback(async (data: IdeaData) => {
    setIsSaving(true);
    try {
      await saveIdeaMutation.mutateAsync(data);
      setSaveMessage("Saved just now");
    } catch (err) {
      setSaveMessage("Error saving");
    } finally {
      setIsSaving(false);
    }
  }, [saveIdeaMutation]);

  const debouncedSave = useDebounceCallback(doSave, 1500);

  const handleChange = (field: keyof IdeaData, value: string) => {
    const newData = { ...formData, [field]: value };
    setFormData(newData);
    setSaveMessage("Saving...");
    debouncedSave(newData);
  };

  const handleAnalyze = async () => {
    try {
      // Final save before analyze
      await saveIdeaMutation.mutateAsync(formData);
      const job = await triggerEvaluationMutation.mutateAsync();
      // Redirect to processing page with the job id
      router.push(`/dashboard/projects/${slug}/processing?jobId=${job.id}`);
    } catch (err) {
      console.error(err);
      alert("Failed to start evaluation.");
    }
  };

  if (!currentProject) {
    return (
      <div className="flex justify-center items-center h-96">
        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/dashboard" className="text-zinc-500 hover:text-white flex items-center gap-1 text-sm font-medium mb-4 transition-colors">
            <ChevronLeft className="w-4 h-4" /> Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-white tracking-tight">Idea Definition</h1>
          <p className="text-zinc-400 mt-1">Project: <span className="text-indigo-400 font-medium">{currentProject.title}</span></p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm font-medium text-zinc-500 flex items-center gap-2">
            {isSaving ? <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> : <Save className="w-4 h-4" />}
            {saveMessage || "Up to date"}
          </div>
          <button
            onClick={handleAnalyze}
            disabled={triggerEvaluationMutation.isPending || saveIdeaMutation.isPending}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-lg font-bold shadow-[0_0_20px_rgba(79,70,229,0.3)] transition-all flex items-center gap-2 disabled:opacity-50"
          >
            {triggerEvaluationMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            Analyze Idea
          </button>
        </div>
      </div>

      <div className="bg-[#0b0b0d] border border-zinc-900 rounded-2xl p-8 space-y-8 shadow-2xl">
        
        {/* Core Concept */}
        <section className="space-y-6">
          <h2 className="text-xl font-bold text-white border-b border-zinc-800 pb-2">1. Core Concept</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-bold text-zinc-300 mb-2">Problem Statement</label>
              <textarea 
                value={formData.problem_statement}
                onChange={e => handleChange("problem_statement", e.target.value)}
                placeholder="What specific problem are you trying to solve?"
                className="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all min-h-[100px]"
              />
            </div>
            
            <div>
              <label className="block text-sm font-bold text-zinc-300 mb-2">Solution Description</label>
              <textarea 
                value={formData.solution_description}
                onChange={e => handleChange("solution_description", e.target.value)}
                placeholder="How does your product solve this problem?"
                className="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all min-h-[100px]"
              />
            </div>
          </div>
        </section>

        {/* Market & Strategy */}
        <section className="space-y-6">
          <h2 className="text-xl font-bold text-white border-b border-zinc-800 pb-2">2. Market & Strategy</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-bold text-zinc-300 mb-2">Target Audience</label>
              <input 
                type="text"
                value={formData.target_audience}
                onChange={e => handleChange("target_audience", e.target.value)}
                placeholder="e.g. B2B SaaS Founders"
                className="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-zinc-300 mb-2">Business Model</label>
              <input 
                type="text"
                value={formData.business_model}
                onChange={e => handleChange("business_model", e.target.value)}
                placeholder="e.g. Subscription ($29/mo)"
                className="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-zinc-300 mb-2">Unique Selling Proposition (USP)</label>
            <textarea 
              value={formData.unique_selling_proposition}
              onChange={e => handleChange("unique_selling_proposition", e.target.value)}
              placeholder="Why are you 10x better than the alternative?"
              className="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 transition-all min-h-[80px]"
            />
          </div>
        </section>

        {/* Technical & Execution */}
        <section className="space-y-6">
          <h2 className="text-xl font-bold text-white border-b border-zinc-800 pb-2">3. Technical & Execution</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-bold text-zinc-300 mb-2">Technology Stack</label>
              <input 
                type="text"
                value={formData.technology_stack}
                onChange={e => handleChange("technology_stack", e.target.value)}
                placeholder="e.g. Next.js, FastAPI, PostgreSQL"
                className="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-zinc-300 mb-2">Timeline / Launch Goal</label>
              <input 
                type="text"
                value={formData.timeline}
                onChange={e => handleChange("timeline", e.target.value)}
                placeholder="e.g. Q4 2026"
                className="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 transition-all"
              />
            </div>
          </div>
        </section>

      </div>
    </div>
  );
}
