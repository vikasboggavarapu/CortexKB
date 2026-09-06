"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  deleteDocument,
  listDocuments,
  type DocumentResponse,
} from "@/lib/api";
import UploadButton from "./UploadButton";

const STATUS_STYLES: Record<string, string> = {
  ready: "bg-green-500/15 text-green-700 dark:text-green-400",
  processing: "bg-brand-peach/60 text-brand-rust",
  failed: "bg-brand-rust/15 text-brand-rust",
  uploaded: "bg-brand-mauve/15 text-brand-mauve",
};

export default function DocumentSidebar({
  selectedIds,
  onSelectionChange,
}: {
  selectedIds: number[];
  onSelectionChange: (ids: number[]) => void;
}) {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const data = await listDocuments();
      setDocuments(data.documents);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    listDocuments()
      .then((data) => {
        if (!cancelled) setDocuments(data.documents);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Failed to load documents");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  function toggle(id: number) {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter((x) => x !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  }

  async function handleDelete(id: number) {
    setDeletingId(id);
    try {
      await deleteDocument(id);
      setDocuments((docs) => docs.filter((d) => d.id !== id));
      onSelectionChange(selectedIds.filter((x) => x !== id));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to delete document");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-border-soft bg-surface-tint">
      <div className="border-b border-border-soft p-4">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-brand-rust">
          Documents
        </h2>
        <UploadButton
          onUploaded={(doc) => setDocuments((docs) => [doc, ...docs])}
          onError={refresh}
        />
      </div>

      <div className="scrollbar-brand flex-1 overflow-y-auto p-2">
        {loading && <p className="p-2 text-sm text-brand-mauve">Loading…</p>}
        {error && (
          <div className="p-2 text-sm text-brand-rust">
            <p>{error}</p>
            <button type="button" onClick={refresh} className="mt-1 font-medium underline">
              Retry
            </button>
          </div>
        )}
        {!loading && documents.length === 0 && !error && (
          <p className="p-2 text-sm text-brand-mauve">
            No documents yet. Upload one to get started.
          </p>
        )}
        <ul className="flex flex-col gap-1">
          {documents.map((doc) => {
            const selected = selectedIds.includes(doc.id);
            return (
              <li
                key={doc.id}
                className={`group flex items-start gap-2 rounded-lg px-2 py-2 transition-colors ${
                  selected ? "bg-brand-peach/60" : "hover:bg-surface"
                }`}
              >
                <input
                  type="checkbox"
                  className="mt-1 shrink-0 accent-brand-coral"
                  checked={selected}
                  disabled={doc.status !== "ready"}
                  onChange={() => toggle(doc.id)}
                />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium" title={doc.filename}>
                    {doc.filename}
                  </p>
                  <span
                    className={`mt-1 inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                      STATUS_STYLES[doc.status] ?? STATUS_STYLES.uploaded
                    }`}
                  >
                    {doc.status}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => handleDelete(doc.id)}
                  disabled={deletingId === doc.id}
                  aria-label={`Delete ${doc.filename}`}
                  className="shrink-0 rounded p-1 text-brand-mauve opacity-0 hover:bg-brand-rust/10 hover:text-brand-rust group-hover:opacity-100 disabled:opacity-50"
                >
                  ✕
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </aside>
  );
}
