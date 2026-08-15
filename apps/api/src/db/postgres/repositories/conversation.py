from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.conversation import Conversation
from .base import BaseRepository


class ConversationRepository(
    BaseRepository[Conversation]
):

    def __init__(self, session: AsyncSession):
        super().__init__(
            session,
            Conversation,
        )

    async def create(
        self,
        user_id: int,
        title: str,
    ) -> Conversation:

        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        self.session.add(conversation)

        await self.session.commit()
        await self.session.refresh(conversation)

        return conversation

    async def get_by_user(
        self,
        user_id: int,
    ) -> list[Conversation]:

        result = await self.session.execute(
            select(Conversation)
            .where(
                Conversation.user_id == user_id
            )
            .order_by(
                Conversation.created_at.desc()
            )
        )

        return list(result.scalars().all())