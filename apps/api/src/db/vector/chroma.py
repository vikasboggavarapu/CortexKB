import asyncio

import chromadb

from config import get_settings

settings = get_settings()

# Module-level singleton — created once, reused across requests
_client: chromadb.ClientAPI | None = None

def get_chroma_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_data_path)
    return _client

async def upsert_document_chunks(
    collection_id: str,
    chunks: list[str],
    embeddings: list[list[float]],
    document_id: int,
) -> None:
    """Upsert all chunks and their embeddings into a per-document collection."""

    def _upsert():
        client = get_chroma_client()
        collection = client.get_or_create_collection(name=collection_id)
        ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
        collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    await asyncio.to_thread(_upsert)

async def delete_document_collection(collection_id: str) -> None:
    """Remove a document's entire ChromaDB collection."""

    def _delete():
        client = get_chroma_client()
        try:
            client.delete_collection(name=collection_id)
        except Exception:
            pass  # collection may not exist if processing failed mid-way

    await asyncio.to_thread(_delete)
