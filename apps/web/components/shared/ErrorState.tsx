import React from "react";
import { AlertTriangle, RefreshCcw } from "lucide-react";
import { Button } from "../ui/button";

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = "Something went wrong",
  message = "An unexpected error occurred. Please try again.",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 border border-red-900/30 rounded-2xl bg-red-950/10">
      <AlertTriangle className="w-12 h-12 text-red-500 mb-4" />
      <h3 className="text-lg font-bold text-red-500 mb-2">{title}</h3>
      <p className="text-red-400/80 text-sm mb-6 text-center max-w-sm">
        {message}
      </p>
      {onRetry && (
        <Button
          onClick={onRetry}
          variant="outline"
          className="border-red-900 text-red-400 hover:bg-red-950"
        >
          <RefreshCcw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      )}
    </div>
  );
}
