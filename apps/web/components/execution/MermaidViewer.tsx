"use client";

import React, { useState, useEffect } from "react";
import { Copy, Check, Download, ZoomIn, ZoomOut, Maximize2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

interface MermaidViewerProps {
  chart: string;
  title?: string;
}

export const MermaidViewer: React.FC<MermaidViewerProps> = ({
  chart,
  title = "Architecture & Execution Diagram",
}) => {
  const [copied, setCopied] = useState(false);
  const [zoom, setZoom] = useState(1);

  const handleCopy = () => {
    navigator.clipboard.writeText(chart);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([chart], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s+/g, "_")}.mmd`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between border-b border-slate-800/80 bg-slate-900/50 py-3 px-4">
        <div className="flex items-center gap-2">
          <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <CardTitle className="text-sm font-semibold text-slate-200">{title}</CardTitle>
          <span className="text-[10px] font-mono uppercase bg-slate-800 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
            Live Mermaid
          </span>
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0 text-slate-400 hover:text-slate-200"
            onClick={() => setZoom((z) => Math.max(0.6, z - 0.15))}
            title="Zoom Out"
          >
            <ZoomOut className="h-3.5 w-3.5" />
          </Button>
          <span className="text-[11px] font-mono text-slate-400 px-1">{Math.round(zoom * 100)}%</span>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0 text-slate-400 hover:text-slate-200"
            onClick={() => setZoom((z) => Math.min(1.8, z + 0.15))}
            title="Zoom In"
          >
            <ZoomIn className="h-3.5 w-3.5" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0 text-slate-400 hover:text-slate-200 ml-1"
            onClick={handleCopy}
            title="Copy Mermaid Code"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0 text-slate-400 hover:text-slate-200"
            onClick={handleDownload}
            title="Download Diagram"
          >
            <Download className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-4 bg-slate-950/80 overflow-x-auto min-h-[220px] flex items-center justify-center">
        <div
          style={{ transform: `scale(${zoom})`, transformOrigin: "center center", transition: "transform 0.15s ease-out" }}
          className="w-full flex justify-center"
        >
          <pre className="p-4 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-indigo-300 max-w-full overflow-x-auto leading-relaxed shadow-inner">
            {chart}
          </pre>
        </div>
      </CardContent>
    </Card>
  );
};
