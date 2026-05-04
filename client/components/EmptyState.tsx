"use client";

import clsx from "clsx";

const SUGGESTIONS = [
  "What pricing plans does NovaSphere offer?",
  "How do I book a demo for your AI platform?",
  "Can you help me reset my account password?",
  "What features are included in the Pro plan?"
];

interface Props {
  onSuggest: (text: string) => void;
}

export default function EmptyState({ onSuggest }: Props) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-12 px-4 text-center">
      <div className="flex flex-col items-center gap-6">
        <div className="w-16 h-16 rounded-2xl bg-zinc-100 flex items-center justify-center text-zinc-950">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 8V4H8" />
            <rect width="16" height="12" x="4" y="8" rx="2" />
            <path d="M2 14h2" />
            <path d="M20 14h2" />
            <path d="M15 13v2" />
            <path d="M9 13v2" />
          </svg>
        </div>

        <div className="space-y-2">
          <h2 className="text-2xl font-semibold text-zinc-100 tracking-tight">
            How can I help you today?
          </h2>
          <p className="text-zinc-500 max-w-sm mx-auto text-sm leading-relaxed">
            I'm a multi-skill agent powered by LangGraph, ready to assist with bookings, pricing, and general inquiries.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => onSuggest(s)}
            className={clsx(
              "text-left p-4 rounded-xl border border-zinc-800 bg-zinc-900/50 transition-all duration-200",
              "hover:border-zinc-700 hover:bg-zinc-900 hover:scale-[1.01] active:scale-[0.99] group"
            )}
          >
            <div className="flex items-center justify-between gap-3">
              <span className="text-sm text-zinc-300 group-hover:text-zinc-100 transition-colors">
                {s}
              </span>
              <svg 
                className="text-zinc-600 group-hover:text-zinc-400 transition-colors flex-shrink-0" 
                width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
              >
                <path d="m9 18 6-6-6-6" />
              </svg>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
