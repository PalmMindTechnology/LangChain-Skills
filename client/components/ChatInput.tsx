"use client";

import { useState, useRef, KeyboardEvent } from "react";
import clsx from "clsx";

interface Props {
  onSend: (text: string) => void;
  isLoading: boolean;
  useStreaming: boolean;
  onToggleStream: (val: boolean) => void;
}

export default function ChatInput({ onSend, isLoading, useStreaming, onToggleStream }: Props) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  };

  return (
    <div className="relative flex flex-col gap-2">
      <div
        className={clsx(
          "relative rounded-2xl border border-zinc-800 bg-zinc-900/50 p-2 transition-all duration-200",
          "focus-within:border-zinc-700 focus-within:bg-zinc-900 focus-within:ring-1 focus-within:ring-zinc-800"
        )}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          placeholder="Message Skills Agent..."
          rows={1}
          disabled={isLoading}
          className={clsx(
            "w-full resize-none bg-transparent px-3 py-2 text-sm leading-relaxed outline-none",
            "placeholder:text-zinc-500 text-zinc-100 min-h-[44px] max-h-[160px]"
          )}
        />

        <div className="flex items-center justify-between px-2 pb-1 pt-1">
          <div className="flex items-center gap-2">
            <button
              onClick={() => onToggleStream(!useStreaming)}
              className={clsx(
                "flex items-center gap-1.5 px-2 py-1 rounded-md text-[10px] font-mono uppercase tracking-wider transition-colors",
                useStreaming ? "text-zinc-100 bg-zinc-800" : "text-zinc-500 hover:text-zinc-400"
              )}
            >
              <div className={clsx(
                "w-1.5 h-1.5 rounded-full",
                useStreaming ? "bg-zinc-100 animate-pulse" : "bg-zinc-600"
              )} />
              Stream
            </button>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-[10px] text-zinc-600 font-mono hidden sm:block">
              ⏎ Send
            </span>
            <button
              onClick={handleSend}
              disabled={!value.trim() || isLoading}
              className={clsx(
                "flex items-center justify-center w-8 h-8 rounded-full transition-all duration-200",
                value.trim() && !isLoading
                  ? "bg-zinc-100 text-zinc-950 hover:bg-zinc-200"
                  : "bg-zinc-800 text-zinc-600 cursor-not-allowed"
              )}
            >
              {isLoading ? (
                <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m5 12 7-7 7 7" />
                  <path d="M12 19V5" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
      <p className="text-[10px] text-center text-zinc-600 px-4">
        Skills Agent can make mistakes. Verify important information.
      </p>
    </div>
  );
}
