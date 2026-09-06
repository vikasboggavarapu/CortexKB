from sqlalchemy.ext.asyncio import AsyncSession

from llm.completion import get_rag_completion
from retrieval.service import retrieve

from .schemas import QueryResponse, SourceChunk

class QueryService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def query(
        self,
        question: str,
        document_ids: list[int],
        top_k: int = 5,
    ) -> QueryResponse:
        # Retrieve relevant chunks
        retrieval = await retrieve(question, document_ids, self.session, top_k)

        if not retrieval.chunks:
            return QueryResponse(
                question=question,
                answer="I could not find any relevant information in the selected documents.",
                sources=[],
            )

        # Extract text for LLM context
        context_chunks = [chunk.text for chunk in retrieval.chunks]

        # Get LLM answer
        answer = await get_rag_completion(question, context_chunks)

        sources = [
            SourceChunk(
                document_id=chunk.document_id,
                text=chunk.text,
                score=chunk.score,
                source=chunk.source,
            )
            for chunk in retrieval.chunks
        ]

        return QueryResponse(
            question=question,
            answer=answer,
            sources=sources,
        )
