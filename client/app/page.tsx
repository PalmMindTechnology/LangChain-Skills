"use client";

import { useEffect, useRef } from "react";
import { useChat } from "@/hooks/useChat";
import MessageBubble from "@/components/MessageBubble";
import ChatInput from "@/components/ChatInput";
import StatusBar from "@/components/StatusBar";
import EmptyState from "@/components/EmptyState";

export default function ChatPage() {
  const {
    messages,
    isLoading,
    useStreaming,
    setUseStreaming,
    sendChat,
    clearMessages,
    threadId,
  } = useChat();

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto w-full px-4 md:px-0">
      {/* Header */}
      <header className="flex items-center justify-between py-4 border-b border-zinc-800/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-zinc-100 flex items-center justify-center text-zinc-950 font-bold text-lg">
            S
          </div>
          <div>
            <h1 className="text-sm font-semibold text-zinc-100">Skills Agent</h1>
            <p className="text-[10px] text-zinc-500 font-mono uppercase tracking-widest">
              LangGraph Core
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <StatusBar threadId={threadId} onClear={clearMessages} />
        </div>
      </header>

      {/* Message list */}
      <main className="flex-1 overflow-y-auto py-8">
        {messages.length === 0 ? (
          <EmptyState onSuggest={(text) => sendChat(text)} />
        ) : (
          <div className="flex flex-col gap-8 pb-4">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}

            {/* Thinking indicator */}
            {isLoading &&
              messages[messages.length - 1]?.role === "assistant" &&
              !messages[messages.length - 1]?.content && (
                <div className="flex gap-1.5 pl-12 py-2">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className="w-1.5 h-1.5 rounded-full bg-zinc-600 animate-pulse"
                      style={{ animationDelay: `${i * 200}ms` }}
                    />
                  ))}
                </div>
              )}

            <div ref={bottomRef} />
          </div>
        )}
      </main>

      {/* Input */}
      <footer className="pb-8 pt-2">
        <ChatInput
          onSend={sendChat}
          isLoading={isLoading}
          useStreaming={useStreaming}
          onToggleStream={setUseStreaming}
        />
      </footer>
    </div>
  );
}
