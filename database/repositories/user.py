"""User repository for database operations."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


class UserRepository:
    """Repository for User model operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language: str = "en",
    ) -> User:
        """Create a new user."""
        user = User(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language=language,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language: str = "en",
    ) -> tuple[User, bool]:
        """Get existing user or create new one. Returns (user, created)."""
        user = await self.get_by_id(user_id)
        if user:
            return user, False

        user = await self.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language=language,
        )
        return user, True

    async def set_language(self, user_id: int, language: str) -> User | None:
        """Update user language preference."""
        await self.session.execute(
            update(User).where(User.id == user_id).values(language=language)
        )
        await self.session.commit()
        return await self.get_by_id(user_id)

    async def get_language(self, user_id: int) -> str:
        """Get user language, defaults to 'en' if not found."""
        user = await self.get_by_id(user_id)
        return user.language if user else "en"
