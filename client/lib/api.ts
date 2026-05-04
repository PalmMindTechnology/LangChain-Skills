import { ChatRequest, ChatResponse, HealthResponse } from "@/types/chat";

const API_BASE = "/api/proxy";

const defaultHeaders = {
  "Content-Type": "application/json",
};

export async function sendMessage(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: defaultHeaders,
    body: JSON.stringify(req),
    signal: AbortSignal.timeout(30000),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP Error: ${res.status}`);
  }

  return await res.json();
}

export async function* streamMessage(
  req: ChatRequest
): AsyncGenerator<string, void, unknown> {
  const res = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: defaultHeaders,
    body: JSON.stringify(req),
    signal: AbortSignal.timeout(60000),
  });

  if (!res.ok || !res.body) {
    const errorText = await res.text().catch(() => res.statusText);
    throw new Error(`Stream request failed: ${res.status} - ${errorText}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split("\n");

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("data: ")) {
          const data = trimmed.slice(6).trim();
          if (data === "[DONE]") return;
          if (data) yield data;
        } else if (trimmed.startsWith("event: error")) {
          throw new Error("Server sent stream error");
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`, {
    method: "GET",
    headers: { Accept: "application/json" },
    cache: "no-store",
    signal: AbortSignal.timeout(100000),
  });

  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return await res.json();
}