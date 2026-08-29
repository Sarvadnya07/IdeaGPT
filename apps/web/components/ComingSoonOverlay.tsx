import React from "react";
import { Construction } from "lucide-react";

interface ComingSoonOverlayProps {
  title: string;
  description: string;
}

export function ComingSoonOverlay({
  title,
  description,
}: ComingSoonOverlayProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4 animate-in fade-in zoom-in duration-500">
      <div className="w-20 h-20 bg-indigo-500/10 border border-indigo-500/20 rounded-full flex items-center justify-center mb-6">
        <Construction className="w-10 h-10 text-indigo-400" />
      </div>
      <h1 className="text-3xl font-bold text-white mb-4">{title}</h1>
      <p className="text-zinc-400 max-w-md mx-auto mb-8 text-sm leading-relaxed">
        {description}
      </p>
      <div className="inline-flex items-center justify-center px-6 py-2 border border-zinc-800 bg-zinc-900/50 rounded-full text-xs font-semibold text-zinc-500 uppercase tracking-widest">
        In Development
      </div>
    </div>
  );
}
