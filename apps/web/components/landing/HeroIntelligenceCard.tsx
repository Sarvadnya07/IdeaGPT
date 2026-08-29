"use client";

import React, { useEffect, useState } from "react";

export function HeroIntelligenceCard() {
  const [pulse, setPulse] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPulse((prev) => (prev + 1) % 100);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative rounded-2xl bg-[#0D0D10] border border-zinc-800/80 shadow-[0_8px_32px_rgba(0,0,0,0.6)] overflow-hidden flex flex-col justify-between h-full group hover:border-zinc-700/80 transition-all">
      {/* Subtle background gradient glow */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-bl from-[#00C29A]/10 via-[#0284C7]/5 to-transparent rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-60 h-60 bg-gradient-to-tr from-[#3B82F6]/10 to-transparent rounded-full blur-2xl pointer-events-none" />

      {/* Header bar */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-zinc-800/70 bg-[#121216]/60 backdrop-blur-sm z-10">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono font-bold tracking-widest text-zinc-400 uppercase">
            AI DECISION INTELLIGENCE
          </span>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold tracking-wide">
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
          </span>
          <span>Live Analysis</span>
        </div>
      </div>

      {/* Futuristic Neural Network / Graph Visualization */}
      <div className="relative w-full h-[230px] sm:h-[260px] flex items-center justify-center p-4 overflow-hidden">
        <svg
          viewBox="0 0 500 240"
          className="w-full h-full object-contain"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="beamGrad" x1="0" y1="120" x2="500" y2="120" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#00C29A" stopOpacity="0.8" />
              <stop offset="50%" stopColor="#00E5FF" stopOpacity="1" />
              <stop offset="100%" stopColor="#3B82F6" stopOpacity="0.8" />
            </linearGradient>

            <linearGradient id="leftCloud" x1="0" y1="0" x2="200" y2="200" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#00C29A" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#0284C7" stopOpacity="0.1" />
            </linearGradient>

            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Background Grid Pattern */}
          <g opacity="0.15">
            <path d="M 0,40 L 500,40 M 0,80 L 500,80 M 0,120 L 500,120 M 0,160 L 500,160 M 0,200 L 500,200" stroke="#38BDF8" strokeWidth="0.5" strokeDasharray="3 3" />
            <path d="M 50,0 L 50,240 M 125,0 L 125,240 M 200,0 L 200,240 M 275,0 L 275,240 M 350,0 L 350,240 M 425,0 L 425,240" stroke="#38BDF8" strokeWidth="0.5" strokeDasharray="3 3" />
          </g>

          {/* Left: Scattered Organic Neural Cluster */}
          <g opacity="0.85">
            {/* Organic connecting lines */}
            <path d="M 60,70 Q 120,40 190,110" stroke="#00C29A" strokeWidth="1" opacity="0.6" />
            <path d="M 40,130 Q 100,110 190,110" stroke="#00C29A" strokeWidth="1.2" opacity="0.7" />
            <path d="M 80,180 Q 130,160 200,130" stroke="#0284C7" strokeWidth="1" opacity="0.5" />
            <path d="M 70,50 L 110,90 L 80,150 L 150,160 L 190,110" stroke="#00C29A" strokeWidth="0.8" opacity="0.4" />
            <path d="M 30,90 L 70,120 L 140,80 L 190,110" stroke="#38BDF8" strokeWidth="0.8" opacity="0.5" />
            <path d="M 90,30 L 150,60 L 190,110" stroke="#00C29A" strokeWidth="0.8" opacity="0.4" />

            {/* Left nodes with glow */}
            <circle cx="60" cy="70" r="3" fill="#00C29A" filter="url(#glow)" />
            <circle cx="40" cy="130" r="3.5" fill="#00E5FF" filter="url(#glow)" />
            <circle cx="80" cy="180" r="2.5" fill="#0284C7" />
            <circle cx="110" cy="90" r="2.5" fill="#00C29A" />
            <circle cx="140" cy="80" r="3" fill="#38BDF8" />
            <circle cx="150" cy="160" r="2.5" fill="#00C29A" />
            <circle cx="90" cy="30" r="2" fill="#00C29A" />
            <circle cx="30" cy="90" r="2" fill="#0284C7" />
            <circle cx="70" cy="120" r="2.5" fill="#00E5FF" />
            <circle cx="150" cy="60" r="2" fill="#38BDF8" />
            <circle cx="170" cy="140" r="2" fill="#00C29A" />
          </g>

          {/* Central Convergence Vortex / Laser Stream */}
          <g filter="url(#glow)">
            <path
              d="M 190,110 Q 240,118 260,120 Q 280,122 330,120"
              stroke="url(#beamGrad)"
              strokeWidth="3.5"
            />
            <path
              d="M 200,130 Q 250,122 260,120 Q 270,118 320,100"
              stroke="url(#beamGrad)"
              strokeWidth="2"
              opacity="0.8"
            />
            <path
              d="M 180,95 Q 240,115 260,120 Q 280,125 325,140"
              stroke="url(#beamGrad)"
              strokeWidth="2"
              opacity="0.8"
            />
            <circle cx="260" cy="120" r="5" fill="#FFFFFF" filter="url(#glow)" />
            <circle cx="260" cy="120" r="8" fill="#00E5FF" opacity="0.5" />
          </g>

          {/* Right: Structured Geometric Lattice / Decision Matrix */}
          <g opacity="0.9">
            {/* Isometric / structured lattice grid lines */}
            <path d="M 330,120 L 380,70 L 440,70 L 470,110 L 440,170 L 380,170 Z" stroke="#3B82F6" strokeWidth="1.2" opacity="0.7" />
            <path d="M 320,100 L 370,50 L 430,50 L 460,90" stroke="#00E5FF" strokeWidth="1" opacity="0.5" />
            <path d="M 325,140 L 375,190 L 435,190 L 465,150" stroke="#00C29A" strokeWidth="1" opacity="0.5" />

            {/* Inner diagonal connecting struts */}
            <path d="M 380,70 L 440,170 M 380,170 L 440,70" stroke="#38BDF8" strokeWidth="0.8" opacity="0.4" />
            <path d="M 330,120 L 410,120 L 470,110" stroke="#00E5FF" strokeWidth="1" opacity="0.6" />
            <path d="M 410,120 L 380,70 M 410,120 L 380,170 M 410,120 L 440,70 M 410,120 L 440,170" stroke="#60A5FA" strokeWidth="0.8" opacity="0.5" />

            {/* Structured Lattice Node points */}
            <circle cx="330" cy="120" r="3.5" fill="#00E5FF" filter="url(#glow)" />
            <circle cx="380" cy="70" r="3" fill="#60A5FA" />
            <circle cx="440" cy="70" r="3" fill="#3B82F6" />
            <circle cx="470" cy="110" r="3.5" fill="#00E5FF" filter="url(#glow)" />
            <circle cx="440" cy="170" r="3" fill="#60A5FA" />
            <circle cx="380" cy="170" r="3" fill="#00C29A" />
            <circle cx="410" cy="120" r="4" fill="#FFFFFF" filter="url(#glow)" />

            <circle cx="370" cy="50" r="2.5" fill="#38BDF8" />
            <circle cx="430" cy="50" r="2.5" fill="#60A5FA" />
            <circle cx="460" cy="90" r="2.5" fill="#3B82F6" />
            <circle cx="375" cy="190" r="2.5" fill="#00C29A" />
            <circle cx="435" cy="190" r="2.5" fill="#38BDF8" />
            <circle cx="465" cy="150" r="2.5" fill="#60A5FA" />
          </g>
        </svg>
      </div>

      {/* Metric Stats Footer Bar */}
      <div className="grid grid-cols-4 gap-2 px-5 py-3.5 border-t border-zinc-800/70 bg-[#121216]/90 backdrop-blur-sm z-10">
        <div>
          <div className="text-[9px] font-mono font-bold tracking-wider text-zinc-400 uppercase">
            DECISION STATUS
          </div>
          <div className="text-xs sm:text-sm font-black text-[#00E599] tracking-tight mt-0.5 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#00E599] animate-pulse"></span>
            NOMINAL
          </div>
        </div>

        <div>
          <div className="text-[9px] font-mono font-bold tracking-wider text-zinc-400 uppercase">
            Confidence
          </div>
          <div className="text-xs sm:text-sm font-black text-white tracking-tight mt-0.5">
            94%
          </div>
        </div>

        <div>
          <div className="text-[9px] font-mono font-bold tracking-wider text-zinc-400 uppercase">
            Risk Level
          </div>
          <div className="text-xs sm:text-sm font-black text-[#00E599] tracking-tight mt-0.5">
            Low
          </div>
        </div>

        <div>
          <div className="text-[9px] font-mono font-bold tracking-wider text-zinc-400 uppercase">
            Evidence
          </div>
          <div className="text-xs sm:text-sm font-black text-white tracking-tight mt-0.5">
            128 <span className="text-[10px] font-normal text-zinc-400">Sources</span>
          </div>
        </div>
      </div>
    </div>
  );
}
