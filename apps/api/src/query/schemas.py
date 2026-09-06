from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    document_ids: list[int] = Field(
        ...,
        min_length=1,
        description="IDs of documents to search against",
    )
    top_k: int = Field(default=5, ge=1, le=20)

class SourceChunk(BaseModel):
    document_id: int
    text: str
    score: float
    source: str  # "semantic" | "keyword" | "semantic+keyword"

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceChunk]