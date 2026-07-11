"use client";

import React, { useEffect } from "react";
import { useSearchParams, useRouter, useParams } from "next/navigation";
import { useEvaluationPolling } from "../../../../../hooks/useEvaluationPolling";
import { Loader2, AlertTriangle, RefreshCcw, CheckCircle2 } from "lucide-react";

export default function ProcessingPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { slug } = useParams();
  
  const jobId = searchParams.get("jobId");
  const { statusQuery, retryMutation } = useEvaluationPolling(jobId ? parseInt(jobId) : null);

  const status = statusQuery.data?.status;

  useEffect(() => {
    if (status === "completed") {
      // Redirect to results dashboard
      setTimeout(() => {
        router.push(`/dashboard/projects/${slug}/results`); // To be implemented in next sprint
      }, 1500);
    }
  }, [status, router, slug]);

  if (!jobId) {
    return <div className="text-white p-8">No Job ID provided.</div>;
  }

  const isFailed = status === "failed" || status === "cancelled";

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] space-y-8">
      
      {!isFailed && status !== "completed" && (
        <div className="relative flex items-center justify-center w-32 h-32">
          <div className="absolute inset-0 border-t-2 border-indigo-500 rounded-full animate-spin"></div>
          <div className="absolute inset-2 border-r-2 border-purple-500 rounded-full animate-spin direction-reverse"></div>
          <Loader2 className="w-8 h-8 text-indigo-400 animate-pulse" />
        </div>
      )}

      {status === "completed" && (
        <div className="w-32 h-32 bg-emerald-500/10 rounded-full flex items-center justify-center animate-in zoom-in duration-500">
          <CheckCircle2 className="w-16 h-16 text-emerald-500" />
        </div>
      )}

      {isFailed && (
        <div className="w-32 h-32 bg-red-500/10 rounded-full flex items-center justify-center">
          <AlertTriangle className="w-16 h-16 text-red-500" />
        </div>
      )}

      <div className="text-center space-y-3">
        <h2 className="text-2xl font-bold text-white capitalize">
          {status === "queued" && "Waiting in Queue..."}
          {status === "processing" && "AI is Evaluating Your Idea..."}
          {status === "completed" && "Evaluation Complete!"}
          {isFailed && "Evaluation Failed"}
        </h2>
        
        <p className="text-zinc-400 max-w-md mx-auto">
          {status === "queued" && "Your request has been received and is waiting for an available worker."}
          {status === "processing" && "Our AI models are analyzing your market fit, generating competitive analysis, and grading potential."}
          {status === "completed" && "Redirecting to your comprehensive report..."}
          {isFailed && (statusQuery.data?.error_message || "An unknown error occurred during generation.")}
        </p>
      </div>

      {isFailed && (
        <button
          onClick={() => retryMutation.mutate()}
          disabled={retryMutation.isPending}
          className="flex items-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-white px-6 py-3 rounded-lg font-bold transition-colors shadow-lg"
        >
          <RefreshCcw className={`w-4 h-4 ${retryMutation.isPending ? "animate-spin" : ""}`} />
          Retry Evaluation
        </button>
      )}

    </div>
  );
}
