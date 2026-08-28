from dataclasses import dataclass
from db.vector.chroma import query_collection,ChunkResult
from llm.embeddings import embed_texts

@dataclass
class SemanticResult:
    document_id: int
    chunk_index : int
    text : str
    score : float
    
async def semantic_search(
    question: str,
    collection_ids: list[str],
    top_k : int = 5,
) -> list[SemanticResult]:

  if not collection_ids:
    return []

  embeddings = await embed_texts([question])
  query_embedding = embeddings[0]

  import asyncio
  tasks = [
    query_collection(collection_id,query_embedding,top_k)
    for collection_id in collection_ids
  ]
  results_per_doc : list[list[ChunkResult]] = await asyncio.gather(*tasks)

  all_chunks: list[SemanticResult] = []
  for chunks in results_per_doc:
    for chunk in chunks:
        all_chunks.append(
            SemanticResult(
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                score = chunk.score,
            )
        )
  all_chunks.sort(key = lambda c: c.score) 
  return all_chunks[:top_k]             
