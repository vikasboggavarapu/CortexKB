from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.refresh_token import RefreshToken
from .base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):

    def __init__(self, session: AsyncSession):
        super().__init__(session, RefreshToken)

    async def create(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def get_valid_by_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
            )
        )
        token = result.scalar_one_or_none()
        if token is None:
            return None

        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at <= datetime.now(timezone.utc):
            return None

        return token

    async def revoke(self, token: RefreshToken) -> None:
        token.revoked = True
        await self.session.commit()
