"use client";

import { useState } from "react";
import AuthGuard from "@/components/AuthGuard";
import DocumentSidebar from "@/components/DocumentSidebar";
import QueryPanel from "@/components/QueryPanel";
import ChatPanel from "@/components/ChatPanel";
import { useAuth } from "@/lib/auth-context";

type Tab = "query" | "chat";

function MainApp() {
  const { user, logout } = useAuth();
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [tab, setTab] = useState<Tab>("query");

  return (
    <div className="flex h-screen flex-col bg-background">
      <header className="flex items-center justify-between border-b border-border-soft bg-surface px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="brand-mark h-8 w-8 rounded-lg" />
          <h1 className="text-lg font-semibold">RAG Assistant</h1>
        </div>
        <div className="flex items-center gap-3 text-sm text-brand-mauve">
          <span>{user?.email}</span>
          <button type="button" onClick={logout} className="btn-outline-brand">
            Log out
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <DocumentSidebar selectedIds={selectedIds} onSelectionChange={setSelectedIds} />

        <main className="flex flex-1 flex-col overflow-hidden">
          <div className="flex gap-1 border-b border-border-soft bg-surface px-6 pt-3">
            {(["query", "chat"] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTab(t)}
                className={`rounded-t-md px-4 py-2 text-sm font-medium capitalize transition-colors ${
                  tab === t
                    ? "border-b-2 border-brand-coral text-brand-coral"
                    : "border-b-2 border-transparent text-brand-mauve hover:text-brand-rust"
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-hidden">
            {tab === "query" ? (
              <QueryPanel documentIds={selectedIds} />
            ) : (
              <ChatPanel documentIds={selectedIds} />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <AuthGuard>
      <MainApp />
    </AuthGuard>
  );
}
