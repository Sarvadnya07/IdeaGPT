import React from "react";

export interface IdeaGPTLogoProps {
  variant?: "full" | "mark" | "wordmark" | "compact";
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
  showSubtitle?: boolean;
}

export function IdeaGPTMark({
  size = "md",
  className = "",
}: {
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  className?: string;
}) {
  const sizeMap = {
    xs: "w-5 h-5",
    sm: "w-7 h-7",
    md: "w-9 h-9",
    lg: "w-12 h-12",
    xl: "w-16 h-16",
  };

  return (
    <div
      className={`relative inline-flex items-center justify-center shrink-0 rounded-xl bg-[#101012] border border-zinc-800/80 shadow-[0_4px_20px_rgba(0,194,154,0.15)] ${sizeMap[size]} ${className}`}
    >
      <svg
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-[78%] h-[78%]"
      >
        <defs>
          <linearGradient
            id="shieldGrad"
            x1="20"
            y1="15"
            x2="80"
            y2="85"
            gradientUnits="userSpaceOnUse"
          >
            <stop offset="0%" stopColor="#00C29A" />
            <stop offset="50%" stopColor="#0284C7" />
            <stop offset="100%" stopColor="#3B82F6" />
          </linearGradient>
          <linearGradient
            id="outerGrad"
            x1="0"
            y1="0"
            x2="100"
            y2="100"
            gradientUnits="userSpaceOnUse"
          >
            <stop offset="0%" stopColor="#2DD4BF" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#0284C7" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#1E3A8A" stopOpacity="0.2" />
          </linearGradient>
        </defs>

        {/* Outer Minimal Geometric Shield Frame */}
        <path
          d="M50 10 L82 26 V52 C82 70 68 84 50 90 C32 84 18 70 18 52 V26 L50 10Z"
          stroke="url(#outerGrad)"
          strokeWidth="6"
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {/* Inner Faceted Decision Shield */}
        <path
          d="M50 24 L70 35 V52 C70 64 61 74 50 78 C39 74 30 64 30 52 V35 L50 24Z"
          fill="url(#shieldGrad)"
        />

        {/* Dynamic Inner Chevron / Transformation Notch */}
        <path d="M50 38 L60 45 L50 64 L40 45 Z" fill="#0C0C0E" opacity="0.9" />
        <path d="M50 44 L55 48 L50 56 L45 48 Z" fill="#00C29A" />
      </svg>
    </div>
  );
}

export function IdeaGPTLogo({
  variant = "full",
  size = "md",
  className = "",
  showSubtitle = true,
}: IdeaGPTLogoProps) {
  if (variant === "mark") {
    return <IdeaGPTMark size={size} className={className} />;
  }

  const textSizes = {
    sm: "text-base tracking-tight",
    md: "text-lg tracking-tight",
    lg: "text-2xl tracking-tighter",
    xl: "text-3xl tracking-tighter",
  };

  const subtitleSizes = {
    sm: "text-[8px]",
    md: "text-[9px]",
    lg: "text-[11px]",
    xl: "text-xs",
  };

  return (
    <div className={`inline-flex items-center gap-3 select-none ${className}`}>
      <IdeaGPTMark size={size} />

      <div className="flex flex-col">
        <div className="flex items-center gap-1.5">
          <span
            className={`font-black text-white font-sans ${textSizes[size]}`}
          >
            IDEA
          </span>
          <span
            className={`font-black bg-clip-text text-transparent bg-gradient-to-r from-teal-400 via-sky-400 to-blue-500 font-sans ${textSizes[size]}`}
          >
            GPT
          </span>
        </div>

        {showSubtitle && variant !== "compact" && (
          <div className="flex items-center gap-1.5 mt-0.5">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-[#00C29A] animate-pulse"></span>
            <span
              className={`font-bold text-zinc-400 uppercase tracking-widest ${subtitleSizes[size]}`}
            >
              STRUCTURED DECISION AI
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
