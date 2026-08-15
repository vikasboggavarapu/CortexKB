from typing import Generic, TypeVar, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..session import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):

    def __init__(
        self,
        session: AsyncSession,
        model: Type[ModelType],
    ):
        self.session = session
        self.model = model

    async def get(self, record_id: int):
        result = await self.session.execute(
            select(self.model).where(
                self.model.id == record_id
            )
        )

        return result.scalar_one_or_none()

    async def delete(self, record_id: int) -> bool:
        record = await self.get(record_id)

        if record is None:
            return False

        await self.session.delete(record)
        await self.session.commit()

        return True