from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from db.postgres.models.user import User
from db.postgres.session import get_db

from .schemas import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
)
from .service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    body: ConversationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Start a new conversation thread."""
    return await ChatService(db).create_conversation(
        user_id=current_user.id,
        title=body.title,
    )

@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all conversations for the current user."""
    return await ChatService(db).list_conversations(current_user.id)

@router.get(
    "/conversations/{conversation_id}/history",
    response_model=list[MessageResponse],
)
async def get_history(
    conversation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get all messages in a conversation."""
    return await ChatService(db).get_history(conversation_id)

@router.post(
    "/conversations/{conversation_id}/message",
    response_model=ChatResponse,
)
async def send_message(
    conversation_id: int,
    body: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Send a message in an existing conversation.
    Retrieves context from the specified documents and returns an LLM answer.
    """
    return await ChatService(db).chat(
        conversation_id=conversation_id,
        question=body.question,
        document_ids=body.document_ids,
        top_k=body.top_k,
    )
