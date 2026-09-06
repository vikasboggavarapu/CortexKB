from datetime import datetime

from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    status: str
    uploaded_by: int
    chroma_collection_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
