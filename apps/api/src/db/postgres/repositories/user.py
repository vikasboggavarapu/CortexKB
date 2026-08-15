from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def create(
        self,
        email: str,
        hashed_password: str,
        role: str = "user",
    ) -> User:

        user = User(
            email=email,
            hashed_password=hashed_password,
            role=role,
        )

        self.session.add(user)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        result = await self.session.execute(
            select(User).where(
                User.email == email
            )
        )

        return result.scalar_one_or_none()