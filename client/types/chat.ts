export type Role = "user" | "assistant";

export interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp: Date;
  loaded_skills?: string[];
  streaming?: boolean;
  error?: boolean;
}

export interface ChatRequest {
  message: string;
  thread_id: string;
}

export interface ChatResponse {
  reply: string;
  thread_id: string;
  loaded_skills: string[];
}

export interface HealthResponse {
  status: string;
  graph_ready: boolean;
}
