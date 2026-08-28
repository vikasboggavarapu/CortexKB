from dataclasses import dataclass

from sqlalchemy import select,text
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres.models.document import Document

@dataclass
class KeywordResult:
    document_id: int
    chroma_collection_id : str
    filename : str
    text: str
    score: float

async def keyword_search(
    question:str,
    document_ids : list[int],
    session: AsyncSession,
    top_k : int = 5,
) -> list[KeywordResult]:

  if not document_ids:
    return []

  stmt = text("""
       SELECT
            id,
            filename,
            chroma_collection_id,
            ts_rank(to_tsvector('english', filename), plainto_tsquery('english', :query)) AS rank
        FROM "Document"
        WHERE
            id = ANY(:doc_ids)
            AND to_tsvector('english', filename) @@ plainto_tsquery('english', :query)
        ORDER BY rank DESC
        LIMIT :top_k
  """)
  result = await session.execute(
    stmt,
    {
        "query": question,
        "doc_ids":document_ids,
        "top_k":top_k,
    },
  )
  rows = result.fetchall()

  return [
    KeywordResult(
        document_id=row.id,
        chroma_collection_id=roww.chroma_collection_id or "",
        filename=row.filename,
        text=f"[Document: {row.filename}]",
        score=float(row.rank),
    )
    for row in rows
  ]    



