from datetime import datetime

from pydantic import BaseModel, Field

# --- Conversation schemas ---

class ConversationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    document_ids: list[int] = Field(
        ...,
        min_length=1,
        description="Documents this conversation is scoped to",
    )

class ConversationResponse(BaseModel):
    id: int
    title: str
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

# --- Message schemas ---

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    sources: list[dict] | None
    created_at: datetime

    model_config = {"from_attributes": True}

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    document_ids: list[int] = Field(
        ...,
        min_length=1,
        description="Documents to search for context",
    )
    top_k: int = Field(default=5, ge=1, le=20)

class ChatResponse(BaseModel):
    conversation_id: int
    question: str
    answer: str
    sources: list[dict]
