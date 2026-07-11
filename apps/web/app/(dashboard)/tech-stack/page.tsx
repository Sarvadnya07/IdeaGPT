"use client";

import React from "react";
import { useIdea } from "../../providers";
import {
  Layers,
  Terminal,
  Database,
  Cloud,
  Cpu,
  ArrowRight,
  TrendingUp,
  GitBranch,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";

interface TechCard {
  title: string;
  tech: string;
  icon: React.ComponentType<any>;
  iconColor: string;
  iconBg: string;
  content: { label?: string; text: string }[];
}

export default function TechStackPage() {
  const { idea } = useIdea();

  // Dynamic stack description
  const stackDescription =
    idea.industry === "DeFi / Web3"
      ? "Based on your requirement for a secure, high-integrity Web3 platform, we recommend a decoupled, robust architecture emphasizing cryptographic safety and advanced state management."
      : "Based on your requirement for a high-concurrency SaaS platform, we recommend a modern, decoupled architecture emphasizing developer velocity and edge-native performance.";

  const techCards: TechCard[] = [
    {
      title: "Frontend",
      tech: idea.industry === "DeFi / Web3" ? "Next.js & RainbowKit" : "Next.js & Tailwind CSS",
      icon: Terminal,
      iconColor: "text-indigo-400",
      iconBg: "bg-indigo-500/10",
      content: [
        {
          label: "WHY THIS STACK?",
          text: "Next.js provides server-side rendering (SSR) crucial for SEO and initial load performance. Tailwind ensures rapid UI iteration with a consistent design system token approach.",
        },
      ],
    },
    {
      title: "Backend Services",
      tech: idea.industry === "DeFi / Web3" ? "Node.js (tRPC) & Rust (Actix)" : "Node.js (tRPC) & Python (Microservices)",
      icon: Layers,
      iconColor: "text-purple-400",
      iconBg: "bg-purple-500/10",
      content: [
        {
          label: "CORE API (NODE):",
          text: "End-to-end type safety with tRPC guarantees frontend-backend synchronization, drastically reducing runtime errors.",
        },
        {
          label: "DATA PROCESSING:",
          text: idea.industry === "DeFi / Web3"
            ? "Rust handles heavy cryptographic proof parsing and ledger interactions with absolute speed and memory safety."
            : "Isolated Python services handle heavy AI inferences and data scraping where ecosystem tooling is vastly superior.",
        },
      ],
    },
    {
      title: "Database",
      tech: idea.industry === "DeFi / Web3" ? "PostgreSQL & PGVector" : "PostgreSQL (Supabase)",
      icon: Database,
      iconColor: "text-emerald-400",
      iconBg: "bg-emerald-500/10",
      content: [
        {
          label: "WHY THIS STACK?",
          text: "Relational integrity with PGVector support out-of-the-box for AI embeddings. Supabase provides instant auth and real-time subscriptions.",
        },
      ],
    },
    {
      title: "Infrastructure",
      tech: "Vercel & AWS",
      icon: Cloud,
      iconColor: "text-sky-400",
      iconBg: "bg-sky-500/10",
      content: [
        {
          label: "WHY THIS STACK?",
          text: "Vercel handles zero-config edge deployments for the frontend. AWS (ECS/S3) provides robust, scalable hosting for backend Python workers and blob storage.",
        },
      ],
    },
    {
      title: "AI Engine",
      tech: "OpenAI GPT-4o & Pinecone",
      icon: Cpu,
      iconColor: "text-rose-400",
      iconBg: "bg-rose-500/10",
      content: [
        {
          label: "WHY THIS STACK?",
          text: "Industry-leading reasoning capabilities coupled with a dedicated vector database for fast, contextual RAG (Retrieval-Augmented Generation) queries.",
        },
      ],
    },
  ];

  return (
    <div className="space-y-8 py-4 select-none">
      {/* Upper header */}
      <div className="space-y-3 border-b border-zinc-900 pb-6">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/10 text-purple-400 border border-purple-500/20 uppercase tracking-widest">
            AI Generated Architecture
          </span>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight text-white">
          Recommended Tech Stack
        </h1>
        <p className="text-sm text-zinc-400 max-w-3xl leading-relaxed">
          {stackDescription}
        </p>
      </div>

      {/* Tech Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {techCards.map((card, idx) => (
          <div
            key={idx}
            className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] hover:border-zinc-800 transition-all flex flex-col justify-between min-h-[260px] group relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-[120px] h-[120px] bg-zinc-800/[0.02] group-hover:bg-zinc-800/[0.05] blur-[40px] pointer-events-none"></div>

            <div className="space-y-4">
              {/* Card Title Header */}
              <div className="flex items-center gap-3">
                <div className={`flex items-center justify-center w-8 h-8 rounded-lg ${card.iconBg} ${card.iconColor}`}>
                  <card.icon className="w-4.5 h-4.5" />
                </div>
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                  {card.title}
                </span>
              </div>

              {/* Main Tech Header */}
              <h3 className="text-base font-extrabold text-white">
                {card.tech}
              </h3>

              {/* Core Descriptions */}
              <div className="space-y-3.5 pt-1">
                {card.content.map((elem, eIdx) => (
                  <div key={eIdx} className="space-y-1">
                    {elem.label && (
                      <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest block">
                        {elem.label}
                      </span>
                    )}
                    <p className="text-[11px] text-zinc-500 leading-relaxed font-medium">
                      {elem.text}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Row 2: Stack Comparison Table & DevOps Pipeline Stepper */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Stack Comparison Card */}
        <div className="lg:col-span-2 bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between">
          <div className="border-b border-zinc-900/60 pb-3 mb-4 flex items-center justify-between">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Stack Comparison
            </h3>
            <span className="text-[9px] text-zinc-500 font-bold uppercase tracking-widest">
              Detailed Breakdown
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-zinc-400 min-w-[500px]">
              <thead>
                <tr className="border-b border-zinc-900 text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                  <th className="py-3 px-2">Metric</th>
                  <th className="py-3 px-2 text-indigo-400">Recommended</th>
                  <th className="py-3 px-2">Alternative (MERN)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-900/60 font-medium">
                {/* Row 1 */}
                <tr className="hover:bg-zinc-900/20">
                  <td className="py-3 px-2 text-[10px] font-bold text-zinc-400 uppercase tracking-wider">
                    Development Speed
                  </td>
                  <td className="py-3 px-2 text-indigo-300">
                    Very High (tRPC, Next.js)
                  </td>
                  <td className="py-3 px-2 text-zinc-600">
                    Moderate (REST overhead)
                  </td>
                </tr>
                {/* Row 2 */}
                <tr className="hover:bg-zinc-900/20">
                  <td className="py-3 px-2 text-[10px] font-bold text-zinc-400 uppercase tracking-wider">
                    Initial Cost
                  </td>
                  <td className="py-3 px-2 text-zinc-300">
                    Low ($0-$20/mo via serverless)
                  </td>
                  <td className="py-3 px-2 text-zinc-600">
                    Low
                  </td>
                </tr>
                {/* Row 3 */}
                <tr className="hover:bg-zinc-900/20">
                  <td className="py-3 px-2 text-[10px] font-bold text-zinc-400 uppercase tracking-wider">
                    Scale Cost
                  </td>
                  <td className="py-3 px-2 text-zinc-300">
                    Moderate (Serverless scaling)
                  </td>
                  <td className="py-3 px-2 text-zinc-600">
                    High (Managing clusters)
                  </td>
                </tr>
                {/* Row 4 */}
                <tr className="hover:bg-zinc-900/20">
                  <td className="py-3 px-2 text-[10px] font-bold text-zinc-400 uppercase tracking-wider">
                    AI Integration
                  </td>
                  <td className="py-3 px-2 text-zinc-300">
                    {idea.industry === "DeFi / Web3"
                      ? "Native (PGVector, Rust backend)"
                      : "Native (PGVector, Python backend)"}
                  </td>
                  <td className="py-3 px-2 text-zinc-600">
                    Requires bolt-on architecture
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* DevOps Pipeline Card */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
          <div className="border-b border-zinc-900/60 pb-3 mb-5">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              DevOps Pipeline
            </h3>
          </div>

          <div className="relative pl-6 border-l border-zinc-800 space-y-6 py-1 ml-2">
            {/* Step 1 */}
            <div className="relative">
              <span className="absolute -left-[30px] top-0 flex items-center justify-center w-5 h-5 rounded-full bg-zinc-900 border border-zinc-800 text-[10px] font-extrabold text-indigo-400 shadow-[0_0_8px_rgba(99,102,241,0.2)] shrink-0">
                1
              </span>
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-white">GitHub Actions (CI)</h4>
                <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                  Automated type checking, linting, and vitest execution on every pull request.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="relative">
              <span className="absolute -left-[30px] top-0 flex items-center justify-center w-5 h-5 rounded-full bg-zinc-900 border border-zinc-800 text-[10px] font-extrabold text-indigo-400 shadow-[0_0_8px_rgba(99,102,241,0.2)] shrink-0">
                2
              </span>
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-white">Preview Environments</h4>
                <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                  Vercel automatically provisions secure preview URLs for active frontend branches.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="relative">
              <span className="absolute -left-[30px] top-0 flex items-center justify-center w-5 h-5 rounded-full bg-zinc-900 border border-zinc-800 text-[10px] font-extrabold text-indigo-400 shadow-[0_0_8px_rgba(99,102,241,0.2)] shrink-0">
                3
              </span>
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-white">Production Deployment</h4>
                <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                  Merge to main triggers zero-downtime deployments to Vercel (Edge) and AWS ECS.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
