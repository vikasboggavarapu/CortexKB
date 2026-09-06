"use client";

import { useRef, useState } from "react";
import { ApiError, uploadDocument, type DocumentResponse } from "@/lib/api";

const ACCEPTED_EXTENSIONS = [".pdf", ".docx", ".csv", ".txt"];

export default function UploadButton({
  onUploaded,
  onError,
}: {
  onUploaded: (doc: DocumentResponse) => void;
  onError?: () => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;

    const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    if (!ACCEPTED_EXTENSIONS.includes(ext)) {
      setError(`Unsupported file type. Accepted: ${ACCEPTED_EXTENSIONS.join(", ")}`);
      return;
    }

    setError(null);
    setUploading(true);
    try {
      const doc = await uploadDocument(file);
      onUploaded(doc);
      if (doc.status === "failed") {
        setError(`"${doc.filename}" failed to process.`);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed");
      // The backend may persist a "failed" document row even when the
      // upload request itself errors out — resync the list to surface it.
      onError?.();
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="flex flex-col gap-1">
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_EXTENSIONS.join(",")}
        onChange={handleChange}
        className="hidden"
        disabled={uploading}
      />
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={uploading}
        className="btn-brand w-full"
      >
        {uploading && (
          <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
        )}
        {uploading ? "Uploading…" : "Upload document"}
      </button>
      {error && <p className="text-xs text-brand-rust">{error}</p>}
    </div>
  );
}
