"use client";

import React, { useState } from "react";
import {
  ExternalLink,
  BookOpen,
  ChevronRight,
  Globe,
  Award,
} from "lucide-react";

export interface CitationItem {
  id: string;
  citation_id?: string;
  title: string;
  url: string;
  domain: string;
  snippet?: string;
  published_at?: string;
  source_type?: string;
  relevance_score?: number;
  is_authoritative?: boolean;
}

interface CitationsDrawerProps {
  citations: CitationItem[];
  className?: string;
}

export const CitationsDrawer: React.FC<CitationsDrawerProps> = ({
  citations,
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!citations || citations.length === 0) {
    return (
      <div className="text-xs text-slate-500 italic">
        No external web citations recorded for this section.
      </div>
    );
  }

  return (
    <div
      className={`border border-white/10 rounded-xl bg-slate-900/50 p-4 ${className}`}
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left text-sm font-semibold text-slate-200 hover:text-white transition"
      >
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-emerald-400" />
          <span>Verified Sources & Citations ({citations.length})</span>
        </div>
        <ChevronRight
          className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? "rotate-90" : ""}`}
        />
      </button>

      {isOpen && (
        <div className="mt-4 space-y-3 pt-3 border-t border-white/5">
          {citations.map((cite, index) => (
            <div
              key={cite.id || index}
              className="p-3 rounded-lg bg-slate-800/60 border border-white/5 hover:border-white/10 transition"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                    {cite.citation_id || `[${index + 1}]`}
                  </span>
                  <a
                    href={cite.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-medium text-slate-200 hover:text-emerald-400 transition flex items-center gap-1.5 line-clamp-1"
                  >
                    {cite.title}
                    <ExternalLink className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                  </a>
                </div>
                {cite.is_authoritative && (
                  <span className="flex-shrink-0 inline-flex items-center gap-1 text-[10px] uppercase font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
                    <Award className="w-3 h-3" /> Authoritative
                  </span>
                )}
              </div>

              {cite.snippet && (
                <p className="mt-1.5 text-xs text-slate-400 line-clamp-2 leading-relaxed">
                  "{cite.snippet}"
                </p>
              )}

              <div className="mt-2 flex items-center gap-3 text-[11px] text-slate-500">
                <span className="flex items-center gap-1">
                  <Globe className="w-3 h-3" /> {cite.domain || "Web Source"}
                </span>
                {cite.published_at && (
                  <span>Published: {cite.published_at}</span>
                )}
                {cite.source_type && <span>Type: {cite.source_type}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
