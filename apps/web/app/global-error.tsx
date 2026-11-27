"use client";

import React, { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Unhandled root layout error:", error);
  }, [error]);

  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-6">
        <div className="max-w-md w-full rounded-xl border border-slate-800 bg-slate-900 p-6 text-center space-y-4">
          <h2 className="text-xl font-semibold text-white">Application Error</h2>
          <p className="text-sm text-slate-400">
            A critical rendering error occurred. Please try reloading the page.
          </p>
          <button
            type="button"
            onClick={() => reset()}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
