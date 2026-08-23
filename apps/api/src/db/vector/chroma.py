from functools import lru_cache

import chromadb
from chromadb import AsyncHttpClient

from config import get_settings

_chroma_client: chromadb.AsyncHttpClient | None = None

async def upsert_document_chunks(
    collection_id: str,
    chunks: list[str],
    embeddings: list[list[float]],
    document_id: int,
) -> None:
    """
    Create (or get) a ChromaDB collection for this document
    and upsert all chunks with their embeddings.
    """
    client = get_chroma_client()
    collection = await client.get_or_create_collection(name=collection_id)

    ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]

    await collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

async def delete_document_collection(collection_id: str) -> None:
    """Remove a document's entire ChromaDB collection on document delete."""
    client = get_chroma_client()
    try:
        await client.delete_collection(name=collection_id)
    except Exception:
        pass  # collection may not exist yet if processing failed
