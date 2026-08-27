"use client";

import React from "react";
import { ShieldCheck, ShieldAlert, Shield } from "lucide-react";

export type ConfidenceLevel = "HIGH" | "MEDIUM" | "LOW";

interface ConfidenceIndicatorProps {
  level: ConfidenceLevel | string;
  className?: string;
  showIcon?: boolean;
}

export const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  level,
  className = "",
  showIcon = true,
}) => {
  const normLevel = (level || "MEDIUM").toUpperCase();

  if (normLevel === "HIGH") {
    return (
      <div className={`inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 ${className}`}>
        {showIcon && <ShieldCheck className="w-3.5 h-3.5" />}
        <span>High Confidence</span>
      </div>
    );
  }

  if (normLevel === "LOW") {
    return (
      <div className={`inline-flex items-center gap-1.5 text-xs font-semibold text-rose-400 ${className}`}>
        {showIcon && <ShieldAlert className="w-3.5 h-3.5" />}
        <span>Low Confidence</span>
      </div>
    );
  }

  return (
    <div className={`inline-flex items-center gap-1.5 text-xs font-semibold text-amber-400 ${className}`}>
      {showIcon && <Shield className="w-3.5 h-3.5" />}
      <span>Medium Confidence</span>
    </div>
  );
};
