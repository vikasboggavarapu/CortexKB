from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres.models.user import User
from db.postgres.repositories.refresh_token import RefreshTokenRepository
from db.postgres.repositories.user import UserRepository

from .schemas import RegisterRequest, TokenResponse, UserResponse
from .utils import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    refresh_token_expires_at,
    verify_password,
)


class AuthService:

    def __init__(self, session: AsyncSession):
        self.users = UserRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)

    async def register(self, data: RegisterRequest) -> UserResponse:
        existing = await self.users.get_by_email(data.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        user = await self.users.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            role="user",
        )
        return UserResponse.model_validate(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        token_hash = hash_token(refresh_token)
        stored_token = await self.refresh_tokens.get_valid_by_hash(token_hash)
        if stored_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user = await self.users.get(stored_token.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        await self.refresh_tokens.revoke(stored_token)
        return await self._issue_tokens(user)

    async def get_user_profile(self, user_id: int) -> UserResponse:
        user = await self.users.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return UserResponse.model_validate(user)

    async def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
        refresh_token = generate_refresh_token()
        await self.refresh_tokens.create(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=refresh_token_expires_at(),
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
