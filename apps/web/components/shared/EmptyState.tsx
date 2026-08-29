import React from "react";
import { FolderX } from "lucide-react";
import { Button } from "../ui/button";

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

export function EmptyState({
  title = "No data found",
  description = "Get started by creating a new entry.",
  actionLabel,
  onAction,
  icon = <FolderX className="w-12 h-12 text-zinc-700" />,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 border border-zinc-800/50 rounded-2xl bg-[#0b0b0d]">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
      <p className="text-zinc-500 text-sm mb-6 text-center max-w-sm">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button
          onClick={onAction}
          variant="default"
          className="bg-indigo-600 hover:bg-indigo-500 text-white"
        >
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
