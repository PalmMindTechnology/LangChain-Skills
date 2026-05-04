"use client";

import { Message } from "@/types/chat";
import clsx from "clsx";

interface Props {
  message: Message;
}

function formatTime(date: Date) {
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div
      className={clsx(
        "message-enter flex gap-4 w-full group",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div className={clsx(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-0.5",
        isUser ? "bg-zinc-800" : "bg-zinc-100"
      )}>
        {isUser ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-zinc-400">
            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-zinc-950">
            <path d="M12 8V4H8" />
            <rect width="16" height="12" x="4" y="8" rx="2" />
            <path d="M2 14h2" />
            <path d="M20 14h2" />
            <path d="M15 13v2" />
            <path d="M9 13v2" />
          </svg>
        )}
      </div>

      <div className={clsx("flex flex-col gap-2 max-w-[85%]", isUser && "items-end")}>
        {/* Bubble */}
        <div
          className={clsx(
            "relative rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
            isUser
              ? "bg-zinc-100 text-zinc-950 font-medium"
              : clsx(
                  "text-zinc-200 bg-zinc-900 border border-zinc-800",
                  message.error && "border-red-900/50 bg-red-950/10 text-red-200"
                )
          )}
        >
          {message.error && (
            <span className="text-red-500 mr-2">⚠</span>
          )}
          <span
            className={clsx(
              "font-sans whitespace-pre-wrap break-words",
              message.streaming && "cursor-blink"
            )}
          >
            {message.content || (message.streaming ? "" : "…")}
          </span>
        </div>

        {/* Skills & Metadata */}
        <div className={clsx("flex items-center gap-3 px-1", isUser && "flex-row-reverse")}>
          {message.loaded_skills && message.loaded_skills.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {message.loaded_skills.map((skill) => (
                <span key={skill} className="skill-pill">
                  {skill}
                </span>
              ))}
            </div>
          )}
          
          <span className="text-[10px] text-zinc-500 font-mono">
            {formatTime(message.timestamp)}
          </span>
        </div>
      </div>
    </div>
  );
}
