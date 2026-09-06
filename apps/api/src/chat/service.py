from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres.repositories.conversation import ConversationRepository
from db.postgres.repositories.message import MessageRepository
from llm.completion import get_chat_completion
from llm.prompts import Message
from retrieval.service import retrieve

from .schemas import (
    ChatResponse,
    ConversationResponse,
    MessageResponse,
)

class ChatService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.conv_repo = ConversationRepository(session)
        self.msg_repo = MessageRepository(session)

    async def create_conversation(
        self,
        user_id: int,
        title: str,
    ) -> ConversationResponse:
        conversation = await self.conv_repo.create(
            user_id=user_id,
            title=title,
        )
        return ConversationResponse.model_validate(conversation)

    async def list_conversations(
        self,
        user_id: int,
    ) -> list[ConversationResponse]:
        conversations = await self.conv_repo.get_by_user(user_id)
        return [ConversationResponse.model_validate(c) for c in conversations]

    async def get_history(
        self,
        conversation_id: int,
    ) -> list[MessageResponse]:
        messages = await self.msg_repo.get_by_conversation(conversation_id)
        return [MessageResponse.model_validate(m) for m in messages]

    async def chat(
        self,
        conversation_id: int,
        question: str,
        document_ids: list[int],
        top_k: int = 5,
    ) -> ChatResponse:
        # Load prior conversation history
        prior_messages = await self.msg_repo.get_by_conversation(conversation_id)
        history = [
            Message(role=m.role, content=m.content)
            for m in prior_messages
        ]

        # Retrieve relevant chunks
        retrieval = await retrieve(question, document_ids, self.session, top_k)
        context_chunks = [chunk.text for chunk in retrieval.chunks]

        if not context_chunks:
            answer = "I could not find any relevant information in the selected documents."
            sources = []
        else:
            answer = await get_chat_completion(question, context_chunks, history)
            sources = [
                {
                    "document_id": chunk.document_id,
                    "text": chunk.text,
                    "score": chunk.score,
                    "source": chunk.source,
                }
                for chunk in retrieval.chunks
            ]

        # Persist user message and assistant answer
        await self.msg_repo.create(
            conversation_id=conversation_id,
            role="user",
            content=question,
        )
        await self.msg_repo.create(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
            sources=sources,
        )

        return ChatResponse(
            conversation_id=conversation_id,
            question=question,
            answer=answer,
            sources=sources,
        )
