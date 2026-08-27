import React from "react";
import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

export type AIStatusType = "analyzing" | "queued" | "completed" | "failed" | "idle";

interface AIStateIndicatorProps {
  status: AIStatusType;
  label?: string;
  className?: string;
  showWaveform?: boolean;
}

export function AIStateIndicator({
  status,
  label,
  className = "",
  showWaveform = true,
}: AIStateIndicatorProps) {
  const getStatusContent = () => {
    switch (status) {
      case "analyzing":
        return {
          defaultText: "Analyzing",
          icon: (
            <div className="flex items-center gap-0.5 h-3">
              <span className="w-1 bg-[#00C29A] h-2.5 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
              <span className="w-1 bg-[#0284C7] h-3.5 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
              <span className="w-1 bg-[#3B82F6] h-2 rounded-full animate-bounce"></span>
            </div>
          ),
          dot: (
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00C29A] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00C29A]"></span>
            </span>
          ),
          containerClass: "bg-[#00C29A]/10 text-[#00C29A] border-[#00C29A]/30 shadow-[0_0_12px_rgba(0,194,154,0.2)]",
        };

      case "queued":
        return {
          defaultText: "Queued",
          icon: <Loader2 className="w-3 h-3 text-amber-400 animate-spin" />,
          dot: <span className="inline-block w-2 h-2 rounded-full bg-amber-400"></span>,
          containerClass: "bg-amber-500/10 text-amber-300 border-amber-500/30",
        };

      case "completed":
        return {
          defaultText: "Completed",
          icon: <CheckCircle2 className="w-3 h-3 text-emerald-400" />,
          dot: <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#10B981]"></span>,
          containerClass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
        };

      case "failed":
        return {
          defaultText: "Failed",
          icon: <AlertCircle className="w-3 h-3 text-red-400" />,
          dot: <span className="inline-block w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_#EF4444]"></span>,
          containerClass: "bg-red-500/10 text-red-400 border-red-500/30",
        };

      case "idle":
      default:
        return {
          defaultText: "Ready",
          icon: <span className="w-1.5 h-1.5 rounded-full bg-zinc-500"></span>,
          dot: <span className="inline-block w-2 h-2 rounded-full bg-zinc-500"></span>,
          containerClass: "bg-zinc-800 text-zinc-400 border-zinc-700",
        };
    }
  };

  const current = getStatusContent();
  const text = label || current.defaultText;

  return (
    <div
      className={`inline-flex items-center gap-2 px-2.5 py-1 rounded-full border text-[11px] font-bold tracking-wide transition-all ${current.containerClass} ${className}`}
    >
      {showWaveform ? current.icon : current.dot}
      <span className="uppercase text-[10px] tracking-wider">{text}</span>
    </div>
  );
}
