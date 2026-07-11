"use client";

import React, { useState } from "react";
import {
  FileText,
  Search,
  ChevronRight,
  Sparkles,
  CheckCircle,
  Play,
  FileDown,
  Edit2,
  List,
  Bold,
  Italic,
  ListOrdered,
} from "lucide-react";
import { toast } from "sonner";

export default function PRDGeneratorPage() {
  const [selectedDocNode, setSelectedDocNode] = useState("overview");
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = () => {
    setIsGenerating(true);
    toast.promise(
      new Promise((resolve) => setTimeout(resolve, 2000)),
      {
        loading: "AI is analyzing requirements and compiling specifications...",
        success: () => {
          setIsGenerating(false);
          return "Comprehensive PRD generated successfully!";
        },
        error: "Failed to generate PRD",
      }
    );
  };

  return (
    <div className="space-y-8 py-4 select-none">
      {/* Top Header bar with Project Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900 pb-5">
        <div className="space-y-1.5 flex items-center gap-3">
          <div>
            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block">
              Project Context
            </span>
            <div className="flex items-center gap-2 mt-0.5">
              <h1 className="text-xl font-extrabold tracking-tight text-white">
                Fintech Dashboard Refactor
              </h1>
              <button className="text-zinc-650 hover:text-zinc-400">
                <Edit2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        <div className="relative max-w-xs w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-zinc-500" />
          </div>
          <input
            type="text"
            placeholder="Search specs..."
            className="block w-full pl-9 pr-3 py-1.5 text-xs text-zinc-300 bg-[#0e0e11] border border-zinc-800 focus:border-indigo-500 rounded-lg outline-none transition-all placeholder:text-zinc-600"
          />
        </div>
      </div>

      {/* Main Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Generator Status & Structure Index */}
        <div className="space-y-6">
          {/* Generator Status */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[170px] relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-[120px] h-[120px] bg-indigo-500/5 blur-[45px] pointer-events-none"></div>

            <div className="flex items-center justify-between border-b border-zinc-900/60 pb-3 mb-4">
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                Generator Status
              </span>
              <span className="inline-flex items-center gap-1 text-[9px] font-bold text-indigo-400 uppercase tracking-wider">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                Ready
              </span>
            </div>

            <div className="space-y-4">
              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="w-full flex items-center justify-center gap-2 py-3 text-xs font-bold text-white bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 active:scale-[0.98] rounded-xl transition-all shadow-[0_4px_15px_rgba(99,102,241,0.25)]"
              >
                <Sparkles className="w-3.5 h-3.5" />
                Generate Full PRD
              </button>
              <div className="text-[9.5px] font-semibold text-zinc-600 uppercase tracking-wide text-center">
                Estimated token cost: ~2,400
              </div>
            </div>
          </div>

          {/* Document Structure Index */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-widest block border-b border-zinc-900 pb-3 mb-4">
              Document Structure
            </span>

            <div className="space-y-1 font-semibold text-xs">
              {/* Item 1 */}
              <div
                onClick={() => setSelectedDocNode("overview")}
                className={`flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                  selectedDocNode === "overview" ? "bg-zinc-900 text-white font-extrabold" : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                <span className="flex items-center gap-2">
                  <FileText className="w-3.5 h-3.5" />
                  Product Overview
                </span>
                <ChevronRight className="w-3.5 h-3.5" />
              </div>

              {/* Item 2 */}
              <div
                onClick={() => setSelectedDocNode("personas")}
                className={`flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                  selectedDocNode === "personas" ? "bg-zinc-900 text-white font-extrabold" : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                <span className="flex items-center gap-2">
                  <FileText className="w-3.5 h-3.5" />
                  User Personas
                </span>
                <ChevronRight className="w-3.5 h-3.5" />
              </div>

              {/* Item 3 */}
              <div
                onClick={() => setSelectedDocNode("features")}
                className={`flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                  selectedDocNode === "features" ? "bg-zinc-900 text-white font-extrabold" : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                <span className="flex items-center gap-2">
                  <FileText className="w-3.5 h-3.5" />
                  Feature Requirements
                </span>
                <ChevronRight className="w-3.5 h-3.5" />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Rich Markdown Editor Canvas */}
        <div className="lg:col-span-2">
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[500px]">
            {/* Editor toolbar */}
            <div className="flex items-center justify-between border-b border-zinc-900 pb-3 mb-6">
              <div className="flex items-center gap-3 text-zinc-500">
                <button className="p-1 rounded hover:text-zinc-300 hover:bg-[#121214]">
                  <Bold className="w-4 h-4" />
                </button>
                <button className="p-1 rounded hover:text-zinc-300 hover:bg-[#121214]">
                  <Italic className="w-4 h-4" />
                </button>
                <button className="p-1 rounded hover:text-zinc-300 hover:bg-[#121214]">
                  <List className="w-4 h-4" />
                </button>
                <button className="p-1 rounded hover:text-zinc-300 hover:bg-[#121214]">
                  <ListOrdered className="w-4 h-4" />
                </button>
              </div>

              <div className="flex items-center gap-4 text-[10px] font-semibold text-zinc-550">
                <span>Last edited 2m ago</span>
                <button
                  onClick={() => toast.success("PRD exported successfully!")}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-[9px] font-bold text-zinc-300 bg-[#070709] border border-zinc-850 hover:bg-zinc-800 rounded-lg uppercase tracking-wider"
                >
                  <FileDown className="w-3 h-3" />
                  Export
                </button>
              </div>
            </div>

            {/* Document display Area */}
            <div className="flex-1 space-y-6 text-zinc-400 font-medium text-xs leading-relaxed max-h-[380px] overflow-y-auto pr-1">
              <h2 className="text-xl font-extrabold text-white">
                Product Overview: Fintech Dashboard
              </h2>

              <div className="space-y-2">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">1. Executive Summary</h3>
                <p className="text-zinc-500">
                  The objective of this PRD is to outline the requirements for a comprehensive refactor of our primary fintech dashboard. This update aims to modernize the user interface, improve data visualization performance for high-frequency trading metrics, and introduce an AI-driven insights module to assist users in making rapid financial decisions.
                </p>
              </div>

              <div className="space-y-2">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">2. Problem Statement</h3>
                <ul className="list-disc pl-4 space-y-1.5 text-zinc-550">
                  <li>Current dashboard load times exceed 3 seconds for large portfolios, leading to user friction.</li>
                  <li>The visual hierarchy lacks clear distinction between actionable alerts and general portfolio performance.</li>
                  <li>Competitor platforms have introduced automated sentiment analysis, causing a feature gap in our offering.</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
