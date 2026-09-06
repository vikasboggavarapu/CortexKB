from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres.repositories.document import DocumentRepository

from .keyword import keyword_search
from .reranker import RankedChunk, rerank
from .semantic import semantic_search

@dataclass
class RetrievalResult:
    chunks: list[RankedChunk]
    document_ids_searched: list[int]

async def retrieve(
    question: str,
    document_ids: list[int],
    session: AsyncSession,
    top_k: int = 5,
) -> RetrievalResult:
    repo = DocumentRepository(session)

    # Fetch only ready documents from the provided IDs
    all_docs = await repo.get_by_user_and_ids(document_ids)
    ready_docs = [d for d in all_docs if d.status == "ready" and d.chroma_collection_id]

    if not ready_docs:
        return RetrievalResult(chunks=[], document_ids_searched=[])

    collection_ids = [d.chroma_collection_id for d in ready_docs]
    ready_doc_ids = [d.id for d in ready_docs]

    # Run sequentially — both share the same AsyncSession which
    # doesn't support concurrent operations on asyncpg
    semantic_results = await semantic_search(question, collection_ids, top_k=top_k)
    keyword_results = await keyword_search(question, ready_doc_ids, session, top_k=top_k)

    ranked = rerank(semantic_results, keyword_results, top_k=top_k)

    return RetrievalResult(
        chunks=ranked,
        document_ids_searched=ready_doc_ids,
    )
