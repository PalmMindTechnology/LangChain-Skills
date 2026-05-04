"use client";

import { useEffect, useState } from "react";
import { checkHealth } from "@/lib/api";
import clsx from "clsx";

interface Props {
  threadId: string;
  onClear: () => void;
}

export default function StatusBar({ threadId, onClear }: Props) {
  const [graphReady, setGraphReady] = useState<boolean | null>(null);

  useEffect(() => {
    checkHealth()
      .then((h) => setGraphReady(h.graph_ready))
      .catch(() => setGraphReady(false));

    const interval = setInterval(() => {
      checkHealth()
        .then((h) => setGraphReady(h.graph_ready))
        .catch(() => setGraphReady(false));
    }, 120_000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-4 text-[10px] font-mono uppercase tracking-wider text-zinc-500">
      <div className="flex items-center gap-1.5">
        <div
          className={clsx(
            "w-1.5 h-1.5 rounded-full",
            graphReady === null ? "bg-zinc-600" : graphReady ? "bg-emerald-500" : "bg-red-500"
          )}
        />
        <span className="hidden sm:inline">
          {graphReady === null ? "Connecting" : graphReady ? "Online" : "Offline"}
        </span>
      </div>

      <div className="flex items-center gap-3">
        <span className="opacity-50 hidden lg:inline">
          ID: {threadId.slice(0, 8)}
        </span>
        <button
          onClick={onClear}
          className="hover:text-zinc-300 transition-colors flex items-center gap-1"
        >
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
          Reset
        </button>
      </div>
    </div>
  );
}
