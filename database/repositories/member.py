"""Member repository for database operations."""

from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Member


class MemberRepository:
    """Repository for Member model operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, member_id: int) -> Member | None:
        """Get member by ID."""
        result = await self.session.execute(
            select(Member).where(Member.id == member_id)
        )
        return result.scalar_one_or_none()

    async def get_by_channel_and_user(
        self, channel_id: int, user_id: int
    ) -> Member | None:
        """Get member by channel and user ID."""
        result = await self.session.execute(
            select(Member).where(
                Member.channel_id == channel_id,
                Member.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_channel_members(
        self, channel_id: int, status: str | None = None
    ) -> list[Member]:
        """Get all members of a channel, optionally filtered by status."""
        query = select(Member).where(Member.channel_id == channel_id)
        if status:
            query = query.where(Member.status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_status(self, channel_id: int) -> dict[str, int]:
        """Count members by status for a channel."""
        result = await self.session.execute(
            select(Member.status, func.count(Member.id))
            .where(Member.channel_id == channel_id)
            .group_by(Member.status)
        )
        return dict(result.all())

    async def create(
        self,
        channel_id: int,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        status: str = "member",
        joined_at: datetime | None = None,
    ) -> Member:
        """Create a new member."""
        member = Member(
            channel_id=channel_id,
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            status=status,
            joined_at=joined_at or datetime.now(),
        )
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def update_status(
        self,
        channel_id: int,
        user_id: int,
        status: str,
        left_at: datetime | None = None,
        **kwargs,
    ) -> Member | None:
        """Update member status."""
        update_data = {"status": status, **kwargs}
        if left_at:
            update_data["left_at"] = left_at

        await self.session.execute(
            update(Member)
            .where(Member.channel_id == channel_id, Member.user_id == user_id)
            .values(**update_data)
        )
        await self.session.commit()
        return await self.get_by_channel_and_user(channel_id, user_id)

    async def upsert(
        self,
        channel_id: int,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        status: str = "member",
    ) -> tuple[Member, bool]:
        """Create or update member. Returns (member, created)."""
        member = await self.get_by_channel_and_user(channel_id, user_id)

        if member:
            # Update existing member
            now = datetime.now()
            update_data = {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "status": status,
            }

            if status in ("left", "kicked", "banned"):
                update_data["left_at"] = now
            elif status == "member" and member.status in ("left", "kicked", "banned"):
                update_data["joined_at"] = now

            await self.session.execute(
                update(Member)
                .where(Member.id == member.id)
                .values(**update_data)
            )
            await self.session.commit()
            await self.session.refresh(member)
            return member, False

        # Create new member
        member = await self.create(
            channel_id=channel_id,
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            status=status,
        )
        return member, True
