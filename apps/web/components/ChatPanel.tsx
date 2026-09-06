"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  ApiError,
  createConversation,
  getConversationHistory,
  listConversations,
  sendMessage,
  type ConversationResponse,
  type MessageResponse,
} from "@/lib/api";

export default function ChatPanel({ documentIds }: { documentIds: number[] }) {
  const [conversations, setConversations] = useState<ConversationResponse[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [input, setInput] = useState("");
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    listConversations()
      .then((data) => {
        if (!cancelled) setConversations(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Failed to load conversations");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const selectConversation = useCallback(async (id: number) => {
    setSelectedId(id);
    setLoadingHistory(true);
    setError(null);
    try {
      const history = await getConversationHistory(id);
      setMessages(history);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load history");
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  function startNewConversation() {
    setSelectedId(null);
    setMessages([]);
    setError(null);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const question = input.trim();
    if (!question || documentIds.length === 0 || sending) return;

    setSending(true);
    setError(null);
    try {
      let conversationId = selectedId;
      if (conversationId === null) {
        const title = question.length > 50 ? `${question.slice(0, 50)}…` : question;
        const conversation = await createConversation(title, documentIds);
        conversationId = conversation.id;
        setSelectedId(conversationId);
        setConversations((prev) => [conversation, ...prev]);
      }

      setInput("");
      await sendMessage(conversationId, question, documentIds);
      const history = await getConversationHistory(conversationId);
      setMessages(history);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to send message");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex h-full">
      <aside className="flex w-56 shrink-0 flex-col border-r border-border-soft bg-surface-tint">
        <div className="border-b border-border-soft p-3">
          <button type="button" onClick={startNewConversation} className="btn-outline-brand w-full">
            + New chat
          </button>
        </div>
        <ul className="scrollbar-brand flex-1 overflow-y-auto p-2">
          {conversations.map((c) => (
            <li key={c.id}>
              <button
                type="button"
                onClick={() => selectConversation(c.id)}
                className={`w-full truncate rounded-lg px-2 py-2 text-left text-sm transition-colors ${
                  selectedId === c.id
                    ? "bg-brand-peach/60 font-medium text-brand-rust"
                    : "text-foreground hover:bg-surface"
                }`}
                title={c.title}
              >
                {c.title}
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <div className="flex flex-1 flex-col bg-background">
        <div className="scrollbar-brand flex-1 overflow-y-auto p-6">
          {loadingHistory && <p className="text-sm text-brand-mauve">Loading…</p>}
          {!loadingHistory && selectedId === null && messages.length === 0 && (
            <p className="text-sm text-brand-mauve">
              Start a new conversation by sending a message below.
            </p>
          )}
          <ul className="flex flex-col gap-4">
            {messages.map((m) => (
              <li
                key={m.id}
                className={`max-w-[75%] whitespace-pre-wrap rounded-2xl px-4 py-2 text-sm shadow-sm ${
                  m.role === "user"
                    ? "ml-auto rounded-br-sm bg-linear-to-br from-brand-coral to-brand-rust text-white"
                    : "rounded-bl-sm bg-surface-tint text-foreground"
                }`}
              >
                {m.content}
              </li>
            ))}
          </ul>
        </div>

        {error && (
          <p className="mx-6 mb-2 rounded-md bg-brand-coral/10 px-3 py-2 text-sm text-brand-rust">
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit} className="flex gap-2 border-t border-border-soft bg-surface p-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              documentIds.length === 0
                ? "Select a document from the sidebar first…"
                : "Send a message…"
            }
            disabled={documentIds.length === 0}
            className="input-brand flex-1"
          />
          <button
            type="submit"
            disabled={sending || documentIds.length === 0 || !input.trim()}
            className="btn-brand"
          >
            {sending ? "Sending…" : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
}
