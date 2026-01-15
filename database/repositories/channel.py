"""Channel repository for database operations."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Channel


class ChannelRepository:
    """Repository for Channel model operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, channel_id: int) -> Channel | None:
        """Get channel by ID."""
        result = await self.session.execute(
            select(Channel).where(Channel.id == channel_id)
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[Channel]:
        """Get all active channels."""
        result = await self.session.execute(
            select(Channel).where(Channel.is_active == True)  # noqa: E712
        )
        return list(result.scalars().all())

    async def get_by_admin(self, admin_user_id: int) -> list[Channel]:
        """Get channels by admin user ID."""
        result = await self.session.execute(
            select(Channel).where(Channel.admin_user_id == admin_user_id)
        )
        return list(result.scalars().all())

    async def create(
        self,
        channel_id: int,
        title: str,
        admin_user_id: int,
        username: str | None = None,
        notify_chat_id: int | None = None,
    ) -> Channel:
        """Create a new channel."""
        channel = Channel(
            id=channel_id,
            title=title,
            username=username,
            admin_user_id=admin_user_id,
            notify_chat_id=notify_chat_id,
            is_active=True,
        )
        self.session.add(channel)
        await self.session.commit()
        await self.session.refresh(channel)
        return channel

    async def update(self, channel_id: int, **kwargs) -> Channel | None:
        """Update channel by ID."""
        await self.session.execute(
            update(Channel).where(Channel.id == channel_id).values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(channel_id)

    async def set_notify_chat(self, channel_id: int, notify_chat_id: int) -> Channel | None:
        """Set notification chat ID for channel."""
        return await self.update(channel_id, notify_chat_id=notify_chat_id)

    async def deactivate(self, channel_id: int) -> None:
        """Deactivate channel."""
        await self.update(channel_id, is_active=False)

    async def get_or_create(
        self,
        channel_id: int,
        title: str,
        admin_user_id: int,
        username: str | None = None,
    ) -> tuple[Channel, bool]:
        """Get existing channel or create new one. Returns (channel, created)."""
        channel = await self.get_by_id(channel_id)
        if channel:
            if not channel.is_active:
                await self.update(channel_id, is_active=True, title=title, username=username)
                channel = await self.get_by_id(channel_id)
            return channel, False

        channel = await self.create(
            channel_id=channel_id,
            title=title,
            admin_user_id=admin_user_id,
            username=username,
        )
        return channel, True
