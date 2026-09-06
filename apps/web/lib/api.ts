import {
  getAccessToken,
  setAccessToken,
  getRefreshToken,
  setRefreshToken,
  clearTokens,
} from "./tokens";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface UserResponse {
  id: number;
  email: string;
  role: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type DocumentStatus = "processing" | "ready" | "failed" | "uploaded";

export interface DocumentResponse {
  id: number;
  filename: string;
  file_type: string;
  status: DocumentStatus;
  uploaded_by: number;
  chroma_collection_id: string | null;
  created_at: string;
}

export interface DocumentListResponse {
  documents: DocumentResponse[];
  total: number;
}

export interface SourceChunk {
  document_id: number;
  text: string;
  score: number;
  source: string;
}

export interface QueryResponse {
  question: string;
  answer: string;
  sources: SourceChunk[];
}

export interface ConversationResponse {
  id: number;
  title: string;
  user_id: number;
  created_at: string;
}

export interface MessageResponse {
  id: number;
  conversation_id: number;
  role: "user" | "assistant";
  content: string;
  sources: SourceChunk[] | null;
  created_at: string;
}

export interface ChatResponse {
  conversation_id: number;
  question: string;
  answer: string;
  sources: SourceChunk[];
}

// ─── Error class ──────────────────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ─── Base fetch ───────────────────────────────────────────────────────────────

const AUTH_ENDPOINTS = new Set(["/auth/login", "/auth/register", "/auth/refresh"]);

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  retry = true,
): Promise<T> {
  const token = getAccessToken();

  const headers: Record<string, string> = {
    ...(options.body instanceof FormData
      ? {}
      : { "Content-Type": "application/json" }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string>),
  };

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  // Auto-refresh on 401 for authenticated calls only — never for the auth
  // endpoints themselves (a bad login/refresh should surface its own error).
  if (response.status === 401 && retry && !AUTH_ENDPOINTS.has(path)) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      return apiFetch<T>(path, options, false); // retry once with new token
    }
    clearTokens();
    throw new ApiError(401, "Session expired. Please log in again.");
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item: { msg?: string }) => item.msg).join(", ")
      : (detail ?? "An error occurred");
    throw new ApiError(response.status, message);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}

async function tryRefresh(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;
  try {
    const data = await apiFetch<TokenResponse>(
      "/auth/refresh",
      {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      },
      false,
    );
    setAccessToken(data.access_token);
    setRefreshToken(data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export async function login(email: string, password: string): Promise<UserResponse> {
  const data = await apiFetch<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setAccessToken(data.access_token);
  setRefreshToken(data.refresh_token);
  return getMe();
}

export async function register(email: string, password: string): Promise<UserResponse> {
  return apiFetch<UserResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function logout(): void {
  clearTokens();
}

export async function getMe(): Promise<UserResponse> {
  return apiFetch<UserResponse>("/auth/me");
}

// ─── Documents ────────────────────────────────────────────────────────────────

export async function listDocuments(): Promise<DocumentListResponse> {
  return apiFetch<DocumentListResponse>("/documents/");
}

export async function uploadDocument(file: File): Promise<DocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return apiFetch<DocumentResponse>("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export async function deleteDocument(documentId: number): Promise<void> {
  return apiFetch<void>(`/documents/${documentId}`, {
    method: "DELETE",
  });
}

// ─── Query ────────────────────────────────────────────────────────────────────

export async function queryDocuments(
  question: string,
  documentIds: number[],
  topK = 5,
): Promise<QueryResponse> {
  return apiFetch<QueryResponse>("/query/", {
    method: "POST",
    body: JSON.stringify({
      question,
      document_ids: documentIds,
      top_k: topK,
    }),
  });
}

// ─── Chat ─────────────────────────────────────────────────────────────────────

export async function createConversation(
  title: string,
  documentIds: number[],
): Promise<ConversationResponse> {
  return apiFetch<ConversationResponse>("/chat/conversations", {
    method: "POST",
    body: JSON.stringify({ title, document_ids: documentIds }),
  });
}

export async function listConversations(): Promise<ConversationResponse[]> {
  return apiFetch<ConversationResponse[]>("/chat/conversations");
}

export async function getConversationHistory(
  conversationId: number,
): Promise<MessageResponse[]> {
  return apiFetch<MessageResponse[]>(
    `/chat/conversations/${conversationId}/history`,
  );
}

export async function sendMessage(
  conversationId: number,
  question: string,
  documentIds: number[],
  topK = 5,
): Promise<ChatResponse> {
  return apiFetch<ChatResponse>(
    `/chat/conversations/${conversationId}/message`,
    {
      method: "POST",
      body: JSON.stringify({
        question,
        document_ids: documentIds,
        top_k: topK,
      }),
    },
  );
}
