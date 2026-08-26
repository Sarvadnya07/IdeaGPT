"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useProjects } from "../../../../hooks/useProjects";
import { ArrowLeft, Loader2, Save } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

export default function NewProjectPage() {
  const router = useRouter();
  const { createProject } = useProjects();
  
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("Other");
  const [isDraftSaved, setIsDraftSaved] = useState(false);

  // Draft Recovery on Mount
  useEffect(() => {
    const draft = localStorage.getItem("project_draft");
    if (draft) {
      try {
        const parsed = JSON.parse(draft);
        setTitle(parsed.title || "");
        setDescription(parsed.description || "");
        setCategory(parsed.category || "Other");
      } catch (e) {}
    }
  }, []);

  // Auto Save Draft
  useEffect(() => {
    const t = setTimeout(() => {
      if (title || description) {
        localStorage.setItem("project_draft", JSON.stringify({ title, description, category }));
        setIsDraftSaved(true);
        setTimeout(() => setIsDraftSaved(false), 2000);
      }
    }, 1000);
    return () => clearTimeout(t);
  }, [title, description, category]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      toast.error("Please provide a project title.");
      return;
    }
    
    try {
      await createProject.mutateAsync({ title: title.trim(), description: description.trim(), category });
      localStorage.removeItem("project_draft"); // Clear draft on success
      toast.success("Project created successfully!");
      router.push("/dashboard");
    } catch (err: any) {
      console.error("Project creation error:", err);
      const detail = err?.response?.data?.detail || "Failed to create project.";
      toast.error(typeof detail === "string" ? detail : "Failed to create project.");
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8">
      <Link href="/dashboard" className="flex items-center gap-2 text-zinc-500 hover:text-white transition-colors mb-8 text-sm">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </Link>
      
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Create New Project</h1>
          <p className="text-zinc-500">Define your idea and initialize a new workspace.</p>
        </div>
        {isDraftSaved && (
          <div className="flex items-center gap-1.5 text-xs text-zinc-500 bg-zinc-900 px-3 py-1.5 rounded-md border border-zinc-800">
            <Save className="w-3 h-3" /> Draft Auto-saved
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 bg-[#0b0b0d] border border-zinc-800/60 p-8 rounded-2xl">
        <div className="space-y-2">
          <label className="text-sm font-medium text-zinc-300">Project Title</label>
          <input
            required
            autoFocus
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500 transition-colors"
            placeholder="e.g. Nexus - AI Development Platform"
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-zinc-300">Category</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500 transition-colors"
          >
            <option value="B2B SaaS">B2B SaaS</option>
            <option value="B2C Consumer">B2C Consumer</option>
            <option value="Fintech">Fintech</option>
            <option value="Healthtech">Healthtech</option>
            <option value="E-commerce">E-commerce</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-zinc-300">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500 transition-colors h-32 resize-none"
            placeholder="Briefly describe what you're building..."
          />
        </div>

        <div className="pt-4 flex justify-end">
          <button
            type="submit"
            disabled={createProject.isPending || !title}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-bold transition-all"
          >
            {createProject.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
            Initialize Workspace
          </button>
        </div>
      </form>
    </div>
  );
}
