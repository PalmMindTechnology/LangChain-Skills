"use client";

import { useState, useCallback, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import { Message } from "@/types/chat";
import { streamMessage, sendMessage } from "@/lib/api";

const THREAD_KEY = "skills_agent_thread_id";

function getOrCreateThreadId(): string {
  if (typeof window === "undefined") return uuidv4();
  const stored = sessionStorage.getItem(THREAD_KEY);
  if (stored) return stored;
  const id = uuidv4();
  sessionStorage.setItem(THREAD_KEY, id);
  return id;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [useStreaming, setUseStreaming] = useState(true);
  const threadId = useRef<string>(getOrCreateThreadId());

  const addMessage = useCallback((msg: Omit<Message, "id" | "timestamp">) => {
    const full: Message = { ...msg, id: uuidv4(), timestamp: new Date() };
    setMessages((prev) => [...prev, full]);
    return full.id;
  }, []);

  const updateMessage = useCallback(
    (id: string, patch: Partial<Message>) => {
      setMessages((prev) =>
        prev.map((m) => (m.id === id ? { ...m, ...patch } : m))
      );
    },
    []
  );

  const sendChat = useCallback(
    async (text: string) => {
      if (!text.trim() || isLoading) return;

      addMessage({ role: "user", content: text });
      setIsLoading(true);

      const assistantId = addMessage({
        role: "assistant",
        content: "",
        streaming: true,
      });

      try {
        if (useStreaming) {
          let accumulated = "";
          for await (const token of streamMessage({
            message: text,
            thread_id: threadId.current,
          })) {
            accumulated += token;
            updateMessage(assistantId, { content: accumulated });
          }
        } else {
          const resp = await sendMessage({
            message: text,
            thread_id: threadId.current,
          });
          updateMessage(assistantId, {
            content: resp.reply,
            loaded_skills: resp.loaded_skills,
          });
        }
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Unknown error";
        updateMessage(assistantId, {
          content: `Error: ${msg}`,
          error: true,
        });
      } finally {
        // Always clear streaming flag, regardless of success or error
        updateMessage(assistantId, { streaming: false });
        setIsLoading(false);
      }
    },
    [isLoading, useStreaming, addMessage, updateMessage]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    const id = uuidv4();
    threadId.current = id;
    sessionStorage.setItem(THREAD_KEY, id);
  }, []);

  return {
    messages,
    isLoading,
    useStreaming,
    setUseStreaming,
    sendChat,
    clearMessages,
    threadId: threadId.current,
  };
}