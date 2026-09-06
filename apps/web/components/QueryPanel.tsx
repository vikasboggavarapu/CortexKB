"use client";

import { useState, type FormEvent } from "react";
import { ApiError, queryDocuments, type QueryResponse } from "@/lib/api";

export default function QueryPanel({ documentIds }: { documentIds: number[] }) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openSources, setOpenSources] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!question.trim() || documentIds.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const data = await queryDocuments(question.trim(), documentIds);
      setResult(data);
      setOpenSources(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full flex-col gap-4 bg-background p-6">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={
            documentIds.length === 0
              ? "Select a document from the sidebar first…"
              : "Ask a question about the selected documents…"
          }
          disabled={documentIds.length === 0}
          className="input-brand flex-1"
        />
        <button
          type="submit"
          disabled={loading || documentIds.length === 0 || !question.trim()}
          className="btn-brand"
        >
          {loading ? "Asking…" : "Ask"}
        </button>
      </form>

      {error && (
        <p className="rounded-md bg-brand-coral/10 px-3 py-2 text-sm text-brand-rust">{error}</p>
      )}

      {result && (
        <div className="card-brand scrollbar-brand flex-1 overflow-y-auto p-5">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-brand-mauve">
            Question
          </p>
          <p className="mb-4 text-sm">{result.question}</p>

          <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-brand-mauve">
            Answer
          </p>
          <p className="mb-4 whitespace-pre-wrap rounded-lg bg-brand-peach/30 p-3 text-sm">
            {result.answer}
          </p>

          {result.sources.length > 0 && (
            <div>
              <button
                type="button"
                onClick={() => setOpenSources((v) => !v)}
                className="text-xs font-semibold text-brand-coral hover:text-brand-rust"
              >
                {openSources ? "Hide" : "Show"} {result.sources.length} source
                {result.sources.length === 1 ? "" : "s"}
              </button>
              {openSources && (
                <ul className="mt-2 flex flex-col gap-2">
                  {result.sources.map((src, i) => (
                    <li
                      key={i}
                      className="rounded-lg border border-border-soft bg-surface-tint p-3 text-xs"
                    >
                      <div className="mb-1 flex items-center justify-between text-brand-mauve">
                        <span>Document #{src.document_id}</span>
                        <span>
                          {src.source} · score {src.score.toFixed(3)}
                        </span>
                      </div>
                      <p className="whitespace-pre-wrap">{src.text}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
