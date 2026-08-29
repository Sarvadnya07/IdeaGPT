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
  Users,
  Target,
  Zap,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";

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
  const [selectedModel, setSelectedModel] = useState<string>(
    "llama-3.3-70b-versatile",
  );
  const [targetRaise, setTargetRaise] = useState<string>("$1.5M Seed");
  const [pitchAngle, setPitchAngle] = useState<string>("");
  const [deckData, setDeckData] = useState<PitchDeckResponse | null>(null);
  const [currentSlideIndex, setCurrentSlideIndex] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isCopied, setIsCopied] = useState<boolean>(false);

  const activeProjectId =
    selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const fetchPitchDeck = async (
    title?: string,
    category?: string,
    description?: string,
    raise?: string,
    angle?: string,
  ) => {
    setIsLoading(true);
    try {
      const projTitle = title || activeProject?.title || "Startup Concept";
      const projCategory = category || activeProject?.category || "B2B SaaS";
      const baseProblem = description || activeProject?.description || "Market lacks specialized intelligence.";
      const prob = angle ? `${baseProblem} (Target raise: ${raise || targetRaise}, angle: ${angle})` : baseProblem;

      const res = await api.post<PitchDeckResponse>("/ai/pitch-deck", {
        title: projTitle,
        category: projCategory,
        problem: prob,
        solution:
          "Automated AI co-founder validating startup concepts and scoping architectures with deterministic unit economics.",
        project_id: activeProjectId || undefined,
        provider: "groq",
        model: selectedModel,
      });
      setDeckData(res.data);
      setCurrentSlideIndex(0);
      toast.success("10-Slide Pitch Deck synthesized with AI!");
    } catch (err) {
      console.error("Failed to load pitch deck:", err);
      toast.error("Failed to generate pitch deck outline.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (activeProject) {
      fetchPitchDeck(
        activeProject.title,
        activeProject.category || "B2B SaaS",
        activeProject.description || "",
      );
    } else if (projects.length === 0 && !projectsQuery.isLoading) {
      fetchPitchDeck("Nexus AI", "B2B SaaS", "AI platform validation");
    }
  }, [activeProjectId]);

  const handleRegenerate = () => {
    fetchPitchDeck(
      activeProject?.title || "Startup Concept",
      activeProject?.category || "B2B SaaS",
      activeProject?.description || "",
      targetRaise,
      pitchAngle,
    );
  };

  const slides = deckData?.slides || [];
  const currentSlide = slides[currentSlideIndex];

  const handleDownloadMarkdown = () => {
    if (!deckData) return;
    const md = `# ${deckData.title} — 10-Slide Investor Pitch Deck
**Category**: ${deckData.category} | **Target Round**: ${targetRaise}

---

${slides
  .map(
    (s) => `## Slide ${s.slide_number}: ${s.title}
### ${s.headline}

${(s.bullet_points || []).map((b) => `- ${b}`).join("\n")}
`,
  )
  .join("\n---\n\n")}
`;

    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${(deckData.title || "pitch-deck").toLowerCase().replace(/[^a-z0-9]+/g, "-")}-pitch-deck.md`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Pitch deck exported to Markdown!");
  };

  const handleCopySlide = () => {
    if (!currentSlide) return;
    const text = `Slide ${currentSlide.slide_number}: ${currentSlide.title}\n${currentSlide.headline}\n\n${(currentSlide.bullet_points || []).join("\n")}`;
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
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Pitch Deck Architect
          </h1>
          <p className="text-neutral-400 text-sm mt-1">
            Structured 10-slide startup narrative covering problem, solution,
            TAM/SAM/SOM, and financial ask.
          </p>
        </div>

        {/* Project Selector & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="bg-neutral-900 border border-neutral-800 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="llama-3.3-70b-versatile">
              Llama 3.3 70B (Groq Fast)
            </option>
            <option value="llama-3.1-8b-instant">
              Llama 3.1 8B Instant (Ultra Fast)
            </option>
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
                  <option
                    key={p.id}
                    value={p.id}
                    className="bg-neutral-900 text-neutral-200"
                  >
                    {p.title}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* REGENERATE BUTTON */}
          <Button
            onClick={handleRegenerate}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition-all shadow-lg shadow-indigo-950/50"
          >
            {isLoading ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            <span>{isLoading ? "Regenerating..." : "Regenerate Deck with AI"}</span>
          </Button>

          {deckData && (
            <Button
              variant="outline"
              onClick={handleDownloadMarkdown}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 border-neutral-700 bg-neutral-900 hover:bg-neutral-800 text-white rounded-lg text-xs font-bold transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export MD</span>
            </Button>
          )}
        </div>
      </div>

      {/* Target Raise & Pitch Tuning */}
      <div className="bg-neutral-900/70 border border-neutral-800 rounded-xl p-3 flex flex-col sm:flex-row items-center gap-3">
        <div className="flex items-center gap-2 shrink-0">
          <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-xs text-neutral-400 font-medium">Target Round:</span>
          <select
            value={targetRaise}
            onChange={(e) => setTargetRaise(e.target.value)}
            className="bg-neutral-950 border border-neutral-800 rounded-md px-2 py-1 text-xs text-emerald-400 font-bold focus:outline-none"
          >
            <option value="$500k Pre-Seed">$500k Pre-Seed</option>
            <option value="$1.5M Seed">$1.5M Seed</option>
            <option value="$3M Seed Plus">$3M Seed Plus</option>
            <option value="$5M Series A">$5M Series A</option>
          </select>
        </div>

        <div className="w-full flex items-center gap-2">
          <input
            type="text"
            value={pitchAngle}
            onChange={(e) => setPitchAngle(e.target.value)}
            placeholder="Custom pitch angle (e.g. AI gross-margin expansion, viral founder network effects)..."
            className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-3 py-1.5 text-xs text-white placeholder:text-neutral-500 focus:outline-none focus:border-indigo-500"
            onKeyDown={(e) => {
              if (e.key === "Enter") handleRegenerate();
            }}
          />
          <Button
            onClick={handleRegenerate}
            disabled={isLoading}
            size="sm"
            variant="secondary"
            className="shrink-0 text-xs h-8 bg-neutral-800 hover:bg-neutral-700 text-white"
          >
            Re-tune
          </Button>
        </div>
      </div>

      {/* Main Content */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24 text-neutral-400 gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-indigo-400" />
          <span className="text-sm font-medium">Crafting 10-Slide Pitch Narrative with AI Gateway...</span>
          <span className="text-xs text-neutral-500">Formatting problem/solution fit, TAM/SAM/SOM, and milestone ask</span>
        </div>
      ) : !deckData || slides.length === 0 ? (
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-12 text-center max-w-lg mx-auto my-12 space-y-4">
          <Presentation className="w-12 h-12 text-neutral-600 mx-auto" />
          <h3 className="text-lg font-bold text-white">No Pitch Deck Generated</h3>
          <p className="text-xs text-neutral-400">
            Click &quot;Regenerate Deck with AI&quot; to synthesize an institutional pitch deck.
          </p>
          <Button
            onClick={handleRegenerate}
            className="bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white"
          >
            <Sparkles className="w-3.5 h-3.5 mr-2" />
            Generate Pitch Deck Now
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start animate-in fade-in duration-300">
          {/* Slide Deck Navigation Sidebar */}
          <div className="lg:col-span-4 space-y-3">
            <div className="flex items-center justify-between px-1">
              <span className="text-xs font-bold text-neutral-400 uppercase tracking-wider">
                10-Slide Overview
              </span>
              <span className="text-xs font-mono text-indigo-400">
                {currentSlideIndex + 1} / {slides.length}
              </span>
            </div>

            <div className="space-y-2 max-h-150 overflow-y-auto pr-1">
              {slides.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentSlideIndex(idx)}
                  className={`w-full text-left p-3.5 rounded-xl border text-xs transition-all flex items-start gap-3 ${
                    currentSlideIndex === idx
                      ? "bg-indigo-950/40 border-indigo-500/50 text-white shadow-md shadow-indigo-950/20"
                      : "bg-neutral-900/60 border-neutral-800 text-neutral-400 hover:text-neutral-200 hover:bg-neutral-900"
                  }`}
                >
                  <span
                    className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] shrink-0 ${
                      currentSlideIndex === idx
                        ? "bg-indigo-600 text-white"
                        : "bg-neutral-800 text-neutral-400"
                    }`}
                  >
                    {s.slide_number}
                  </span>
                  <div className="truncate">
                    <div className="font-semibold truncate">{s.title}</div>
                    <div className="text-[11px] text-neutral-500 truncate mt-0.5">
                      {s.headline}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Active Slide Presentation Canvas */}
          <div className="lg:col-span-8 space-y-4">
            {currentSlide && (
              <div className="bg-neutral-900 border border-neutral-800 rounded-3xl p-8 md:p-12 space-y-8 min-h-[480px] flex flex-col justify-between relative shadow-2xl">
                {/* Slide Header */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-full text-xs font-mono font-bold">
                      SLIDE {currentSlide.slide_number} OF {slides.length}
                    </span>
                    <button
                      onClick={handleCopySlide}
                      className="inline-flex items-center gap-1.5 text-xs text-neutral-400 hover:text-white transition-colors bg-neutral-800/80 px-3 py-1.5 rounded-lg border border-neutral-700/50"
                    >
                      {isCopied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{isCopied ? "Copied" : "Copy Slide"}</span>
                    </button>
                  </div>

                  <h2 className="text-3xl md:text-4xl font-black text-white tracking-tight pt-2">
                    {currentSlide.title}
                  </h2>
                  <p className="text-sm md:text-base text-neutral-400 font-medium">
                    {currentSlide.headline}
                  </p>
                </div>

                {/* Bullet Points */}
                <div className="space-y-4 my-6">
                  {(currentSlide.bullet_points || []).map((bullet, bIdx) => (
                    <div
                      key={bIdx}
                      className="flex items-start gap-4 p-4 rounded-xl bg-neutral-950/60 border border-neutral-800/80"
                    >
                      <CheckCircle2 className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
                      <p className="text-xs md:text-sm text-neutral-200 leading-relaxed font-normal">
                        {bullet}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Slide Controls Footer */}
                <div className="flex items-center justify-between border-t border-neutral-800 pt-6 mt-6">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={currentSlideIndex === 0}
                    onClick={() =>
                      setCurrentSlideIndex((prev) => Math.max(0, prev - 1))
                    }
                    className="border-neutral-800 text-neutral-300 hover:bg-neutral-800 text-xs"
                  >
                    <ChevronLeft className="w-4 h-4 mr-1" />
                    <span>Previous</span>
                  </Button>

                  <span className="text-xs font-mono text-neutral-500">
                    {deckData.title} • {targetRaise}
                  </span>

                  <Button
                    variant="outline"
                    size="sm"
                    disabled={currentSlideIndex === slides.length - 1}
                    onClick={() =>
                      setCurrentSlideIndex((prev) =>
                        Math.min(slides.length - 1, prev + 1),
                      )
                    }
                    className="border-neutral-800 text-neutral-300 hover:bg-neutral-800 text-xs"
                  >
                    <span>Next</span>
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
