"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useProjects } from "@/hooks/useProjects";
import { useApiClient } from "@/lib/api/client";
import {
  Presentation,
  Layers,
  Sparkles,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Download,
  Copy,
  Check,
  CheckCircle2,
  TrendingUp,
  DollarSign,
  Users
} from "lucide-react";
import { toast } from "sonner";

interface SlideItem {
  slide_number: number;
  title: string;
  headline: string;
  bullet_points: string[];
}

interface PitchDeckResponse {
  title: string;
  category: string;
  slides: SlideItem[];
}

export default function PitchDeckPage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects({ limit: 50 });
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [selectedModel, setSelectedModel] = useState<string>("llama-3.3-70b-versatile");
  const [deckData, setDeckData] = useState<PitchDeckResponse | null>(null);
  const [currentSlideIndex, setCurrentSlideIndex] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isCopied, setIsCopied] = useState<boolean>(false);

  const activeProjectId = selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const fetchPitchDeck = async (title: string, category: string, description: string) => {
    setIsLoading(true);
    try {
      const res = await api.post<PitchDeckResponse>("/ai/pitch-deck", {
        title: title || "Startup Concept",
        category: category || "B2B SaaS",
        problem: description || "",
        solution: "Automated AI co-founder validating startup concepts and scoping architectures.",
        provider: "groq",
        model: selectedModel,
      });
      setDeckData(res.data);
      setCurrentSlideIndex(0);
    } catch (err) {
      console.error("Failed to load pitch deck:", err);
      toast.error("Failed to generate pitch deck outline.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (activeProject) {
      fetchPitchDeck(activeProject.title, activeProject.category || "B2B SaaS", activeProject.description || "");
    } else if (projects.length === 0 && !projectsQuery.isLoading) {
      fetchPitchDeck("Nexus AI", "B2B SaaS", "AI platform validation");
    }
  }, [activeProjectId]);

  const slides = deckData?.slides || [];
  const currentSlide = slides[currentSlideIndex];

  const handleDownloadMarkdown = () => {
    if (!deckData) return;
    const md = `# ${deckData.title} — 10-Slide Investor Pitch Deck
**Category**: ${deckData.category}  

---

${slides
  .map(
    (s) => `## Slide ${s.slide_number}: ${s.title}
### ${s.headline}

${s.bullet_points.map((b) => `- ${b}`).join("\n")}
`
  )
  .join("\n---\n\n")}
`;

    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${deckData.title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-pitch-deck.md`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Pitch deck exported!");
  };

  const handleCopySlide = () => {
    if (!currentSlide) return;
    const text = `Slide ${currentSlide.slide_number}: ${currentSlide.title}\n${currentSlide.headline}\n\n${currentSlide.bullet_points.join("\n")}`;
    navigator.clipboard.writeText(text);
    setIsCopied(true);
    toast.success(`Copied Slide ${currentSlide.slide_number} to clipboard!`);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-6 md:p-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-neutral-800 pb-6">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-medium text-sm mb-1">
            <Presentation className="w-4 h-4" />
            <span>Venture Pitch Deck Generator</span>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Pitch Deck Architect</h1>
          <p className="text-neutral-400 text-sm mt-1">
            Structured 10-slide startup narrative covering problem, solution, TAM/SAM/SOM, and financial ask.
          </p>
        </div>

        {/* Project Selector & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedModel}
            onChange={(e) => {
              setSelectedModel(e.target.value);
              if (activeProject) fetchPitchDeck(activeProject.title, activeProject.category || "B2B SaaS", activeProject.description || "");
            }}
            className="bg-neutral-900 border border-neutral-800 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="llama-3.3-70b-versatile">Llama 3.3 70B Versatile (Groq)</option>
            <option value="qwen/qwen3.8-27b">Qwen 3.8 27B (Groq)</option>
            <option value="openai/gpt-oss-20b">GPT-OSS 20B (Groq)</option>
          </select>
          {projects.length > 0 && (
            <div className="flex items-center gap-2 bg-neutral-900 border border-neutral-800 rounded-lg p-2">
              <Layers className="w-4 h-4 text-neutral-400 ml-1" />
              <select
                value={activeProjectId}
                onChange={(e) => setSelectedProjectId(e.target.value)}
                className="bg-transparent text-xs text-neutral-200 focus:outline-none cursor-pointer pr-2"
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id} className="bg-neutral-900 text-neutral-200">
                    {p.title}
                  </option>
                ))}
              </select>
            </div>
          )}

          {deckData && (
            <button
              onClick={handleDownloadMarkdown}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition-colors shadow-lg shadow-indigo-950/50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Deck</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-24 text-neutral-400 gap-3">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
          <span>Structuring 10-slide investor pitch deck...</span>
        </div>
      ) : !deckData || slides.length === 0 ? (
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-12 text-center max-w-lg mx-auto my-12 space-y-4">
          <Presentation className="w-12 h-12 text-neutral-600 mx-auto" />
          <h3 className="text-lg font-bold text-white">No Pitch Deck Available</h3>
          <p className="text-xs text-neutral-400">Select a project to generate a tailored pitch deck.</p>
        </div>
      ) : (
        <div className="space-y-8 animate-in fade-in duration-300 max-w-5xl mx-auto">
          {/* Active Slide Presentation View */}
          {currentSlide && (
            <div className="bg-gradient-to-br from-neutral-900 via-neutral-900 to-indigo-950/40 border border-neutral-800 rounded-2xl p-8 md:p-12 shadow-2xl min-h-[380px] flex flex-col justify-between space-y-6 relative overflow-hidden">
              <div className="space-y-4">
                <div className="flex items-center justify-between text-xs font-mono text-indigo-400 border-b border-neutral-800 pb-3">
                  <span className="font-bold uppercase tracking-widest">
                    Slide {currentSlide.slide_number} of {slides.length} • {currentSlide.title}
                  </span>
                  <span className="text-neutral-500">{deckData.title}</span>
                </div>

                <h2 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
                  {currentSlide.headline}
                </h2>

                <div className="space-y-3 pt-4">
                  {currentSlide.bullet_points.map((pt, i) => (
                    <div key={i} className="flex items-start gap-3 text-sm text-neutral-200 leading-relaxed">
                      <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-2 shrink-0" />
                      <span>{pt}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Navigation Controls inside Slide */}
              <div className="flex items-center justify-between pt-6 border-t border-neutral-800/80">
                <button
                  onClick={() => setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1))}
                  disabled={currentSlideIndex === 0}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-neutral-800 hover:bg-neutral-700 disabled:opacity-30 disabled:cursor-not-allowed text-white rounded-xl text-xs font-semibold transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span>Previous Slide</span>
                </button>

                <div className="flex items-center gap-1.5">
                  {slides.map((_, idx) => (
                    <button
                      key={idx}
                      onClick={() => setCurrentSlideIndex(idx)}
                      className={`w-2.5 h-2.5 rounded-full transition-all ${
                        currentSlideIndex === idx ? "bg-indigo-500 w-6" : "bg-neutral-700 hover:bg-neutral-500"
                      }`}
                    />
                  ))}
                </div>

                <button
                  onClick={() => setCurrentSlideIndex(Math.min(slides.length - 1, currentSlideIndex + 1))}
                  disabled={currentSlideIndex === slides.length - 1}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 disabled:cursor-not-allowed text-white rounded-xl text-xs font-semibold transition-colors"
                >
                  <span>Next Slide</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* Slide Deck Grid Thumbnails */}
          <div className="space-y-4 pt-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider text-neutral-400">
              All 10 Slides Overview
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {slides.map((s, idx) => (
                <div
                  key={s.slide_number}
                  onClick={() => setCurrentSlideIndex(idx)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer space-y-1.5 ${
                    currentSlideIndex === idx
                      ? "bg-indigo-950/60 border-indigo-500 text-white ring-1 ring-indigo-500/30"
                      : "bg-neutral-900/80 border-neutral-800 hover:border-neutral-700 text-neutral-400"
                  }`}
                >
                  <div className="text-[10px] font-mono font-bold text-indigo-400">#{s.slide_number}</div>
                  <div className="text-xs font-semibold text-white line-clamp-1">{s.title}</div>
                  <p className="text-[11px] text-neutral-400 line-clamp-2">{s.headline}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
