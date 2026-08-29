"use client";

import React, { useState } from "react";
import { Mic, Copy, Check, Sparkles, MessageSquare, Users, Briefcase } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export interface PitchVariant {
  variant_type: string;
  label: string;
  target_audience: string;
  pitch_text: string;
}

interface ElevatorPitchVariantsProps {
  variants?: PitchVariant[];
  ideaTitle?: string;
}

export const ElevatorPitchVariants: React.FC<ElevatorPitchVariantsProps> = ({
  variants = [
    {
      variant_type: "10_WORD",
      label: "10-Word Teaser",
      target_audience: "Social Media / Intro Badges",
      pitch_text: "IdeaGPT: Evidence-grounded startup decision intelligence for high-velocity founders."
    },
    {
      variant_type: "ONE_SENTENCE",
      label: "One-Sentence Value Prop",
      target_audience: "General Networking",
      pitch_text: "For founders navigating ambiguous markets, IdeaGPT turns raw concepts into verifiable research, deterministic unit economics, and execution roadmaps in seconds."
    },
    {
      variant_type: "FOUNDER_PITCH",
      label: "Founder to Founder",
      target_audience: "Peer Builders & Co-Founders",
      pitch_text: "We built IdeaGPT because guesswork burns precious founder runway. Our multi-agent intelligence layer stress-tests assumptions and builds institutional-grade strategy before writing a line of code."
    },
    {
      variant_type: "INVESTOR_PITCH",
      label: "Investor Pitch",
      target_audience: "Venture Capital & Angels",
      pitch_text: "IdeaGPT captures the $4.2B venture intelligence market with an AI-gateway decision engine featuring strong switching costs, verified citations, and 85%+ gross margins."
    }
  ],
  ideaTitle = "Startup Venture"
}) => {
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl">
      <CardHeader className="border-b border-slate-800/80 bg-slate-900/50 py-4 px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Mic className="h-5 w-5 text-indigo-400" />
            <CardTitle className="text-base font-bold text-slate-100">
              Elevator Pitch Variants
            </CardTitle>
          </div>
          <span className="text-[10px] font-mono uppercase bg-slate-800 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
            Multi-Audience Framing
          </span>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-4">
        {variants.map((v, idx) => (
          <div
            key={idx}
            className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-colors space-y-2"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">{v.label}</span>
                <span className="text-[11px] text-slate-500">• {v.target_audience}</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 px-2 text-xs text-slate-400 hover:text-slate-200"
                onClick={() => handleCopy(v.pitch_text, idx)}
              >
                {copiedIdx === idx ? <Check className="h-3.5 w-3.5 text-emerald-400 mr-1" /> : <Copy className="h-3.5 w-3.5 mr-1" />}
                <span>{copiedIdx === idx ? "Copied" : "Copy"}</span>
              </Button>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-medium">"{v.pitch_text}"</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
