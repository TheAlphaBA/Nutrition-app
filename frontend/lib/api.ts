/**
 * NutriBot API Client
 * Connects the Next.js frontend with the FastAPI backend.
 */

export interface Claim {
  id?: string;
  text: string;
  source: string | null;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  claims?: Claim[];
  guardrail_triggered?: boolean;
  guardrail_reason?: string | null;
}

export interface ConversationSummary {
  id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  preview: string;
}

export interface ConversationDetail {
  id: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ChatResponse {
  conversation_id: string;
  message_id: string;
  answer: string;
  claims: Claim[];
  guardrail_triggered: boolean;
  guardrail_reason: string | null;
}

export function getApiBase(): string {
  let url = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api").trim();
  // Strip trailing slashes
  url = url.replace(/\/+$/, "");
  // If user omitted protocol
  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    url = `https://${url}`;
  }
  // Strip accidental trailing /chat
  if (url.endsWith("/chat")) {
    url = url.slice(0, -5).replace(/\/+$/, "");
  }
  // Ensure it ends with /api
  if (!url.endsWith("/api")) {
    url = `${url}/api`;
  }
  return url;
}

export const API_BASE = getApiBase();

export async function fetchConversations(): Promise<ConversationSummary[]> {
  try {
    const res = await fetch(`${API_BASE}/conversations`, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch conversations:", err);
    return [];
  }
}

export async function fetchConversation(id: string): Promise<ConversationDetail | null> {
  try {
    const res = await fetch(`${API_BASE}/conversations/${id}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Failed to fetch conversation ${id}:`, err);
    return null;
  }
}

export async function sendChatMessage(
  message: string,
  conversationId?: string | null
): Promise<ChatResponse> {
  const payload: { message: string; conversation_id?: string } = { message };
  if (conversationId) {
    payload.conversation_id = conversationId;
  }

  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Server error (HTTP ${res.status})`);
  }

  return await res.json();
}

export async function checkBackendHealth(): Promise<{ status: string; environment?: string }> {
  try {
    const baseUrl = API_BASE.replace(/\/api$/, "");
    const res = await fetch(`${baseUrl}/health`, { cache: "no-store" });
    if (!res.ok) return { status: "offline" };
    return await res.json();
  } catch {
    return { status: "offline" };
  }
}
