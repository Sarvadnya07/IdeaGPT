"use client";

import React, { useState, useEffect, useRef } from "react";
import { Copy, Check, Download, ZoomIn, ZoomOut, RotateCcw, Code2, Eye, AlertCircle } from "lucide-react";
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
  const [viewMode, setViewMode] = useState<"diagram" | "code">("diagram");
  const [svgContent, setSvgContent] = useState<string | null>(null);
  const [renderError, setRenderError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Render Mermaid diagram to SVG client-side
  useEffect(() => {
    let isMounted = true;

    async function renderChart() {
      if (!chart || typeof window === "undefined") return;

      try {
        setRenderError(null);
        const mermaid = (await import("mermaid")).default;
        
        mermaid.initialize({
          startOnLoad: false,
          theme: "dark",
          themeVariables: {
            darkMode: true,
            background: "#090d16",
            primaryColor: "#4f46e5",
            primaryTextColor: "#f8fafc",
            primaryBorderColor: "#6366f1",
            lineColor: "#818cf8",
            secondaryColor: "#1e1b4b",
            tertiaryColor: "#0f172a",
          },
          securityLevel: "loose",
          flowchart: {
            curve: "basis",
            htmlLabels: true,
          },
        });

        // Clean chart string
        const cleanChart = chart.trim();
        const id = `mermaid-svg-${Math.random().toString(36).substring(2, 9)}`;
        const { svg } = await mermaid.render(id, cleanChart);

        if (isMounted) {
          setSvgContent(svg);
        }
      } catch (err: any) {
        console.warn("Mermaid rendering warning (falling back to code viewer):", err);
        if (isMounted) {
          setRenderError(err?.message || "Diagram syntax could not be rendered as SVG");
        }
      }
    }

    renderChart();

    return () => {
      isMounted = false;
    };
  }, [chart]);

  const handleCopy = () => {
    navigator.clipboard.writeText(chart);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadSvg = () => {
    if (svgContent) {
      const blob = new Blob([svgContent], { type: "image/svg+xml" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${title.toLowerCase().replace(/[^a-z0-9]+/g, "_")}.svg`;
      a.click();
      URL.revokeObjectURL(url);
    } else {
      const blob = new Blob([chart], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${title.toLowerCase().replace(/[^a-z0-9]+/g, "_")}.mmd`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <Card className="border border-slate-800 bg-slate-950 text-slate-100 shadow-xl overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between border-b border-slate-800/80 bg-slate-900/50 py-3 px-4 flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <div className="h-2.5 w-2.5 rounded-full bg-indigo-500 animate-pulse" />
          <CardTitle className="text-sm font-semibold text-slate-200">{title}</CardTitle>
          <span className="text-[10px] font-mono uppercase bg-slate-800 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
            Interactive Visual Diagram
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          {/* Mode Switcher */}
          <div className="flex items-center bg-slate-900 rounded-lg p-0.5 border border-slate-800 mr-1">
            <button
              onClick={() => setViewMode("diagram")}
              className={`px-2 py-1 rounded text-[11px] font-medium flex items-center gap-1 transition-colors ${
                viewMode === "diagram" ? "bg-indigo-600 text-white font-bold" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Eye className="h-3 w-3" />
              <span>Diagram</span>
            </button>
            <button
              onClick={() => setViewMode("code")}
              className={`px-2 py-1 rounded text-[11px] font-medium flex items-center gap-1 transition-colors ${
                viewMode === "code" ? "bg-indigo-600 text-white font-bold" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Code2 className="h-3 w-3" />
              <span>Source</span>
            </button>
          </div>

          {/* Zoom Controls (Diagram Mode) */}
          {viewMode === "diagram" && (
            <div className="flex items-center gap-1 border-l border-slate-800 pl-2">
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0 text-slate-400 hover:text-slate-200"
                onClick={() => setZoom((z) => Math.max(0.5, z - 0.15))}
                title="Zoom Out"
              >
                <ZoomOut className="h-3.5 w-3.5" />
              </Button>
              <span className="text-[11px] font-mono text-slate-400 px-1 min-w-[36px] text-center">
                {Math.round(zoom * 100)}%
              </span>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0 text-slate-400 hover:text-slate-200"
                onClick={() => setZoom((z) => Math.min(2.0, z + 0.15))}
                title="Zoom In"
              >
                <ZoomIn className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0 text-slate-400 hover:text-slate-200"
                onClick={() => setZoom(1)}
                title="Reset Zoom"
              >
                <RotateCcw className="h-3 w-3" />
              </Button>
            </div>
          )}

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
            onClick={handleDownloadSvg}
            title="Download Diagram (SVG/MMD)"
          >
            <Download className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-6 bg-slate-950 min-h-[320px] flex items-center justify-center overflow-auto relative">
        {viewMode === "code" || (renderError && !svgContent) ? (
          <div className="w-full space-y-3">
            {renderError && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-amber-950/30 border border-amber-500/20 text-amber-300 text-xs">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>Showing formatted Mermaid source code representation.</span>
              </div>
            )}
            <pre className="p-5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-indigo-300 w-full overflow-x-auto leading-relaxed shadow-inner">
              {chart}
            </pre>
          </div>
        ) : (
          <div
            ref={containerRef}
            style={{
              transform: `scale(${zoom})`,
              transformOrigin: "top center",
              transition: "transform 0.15s ease-out",
            }}
            className="w-full flex justify-center py-4 [&_svg]:max-w-full [&_svg]:h-auto [&_svg]:rounded-xl [&_svg]:filter [&_svg]:drop-shadow-md"
            dangerouslySetInnerHTML={{ __html: svgContent || `<pre class="text-xs font-mono text-indigo-300">${chart}</pre>` }}
          />
        )}
      </CardContent>
    </Card>
  );
};
