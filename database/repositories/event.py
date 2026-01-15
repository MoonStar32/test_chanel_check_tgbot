"""Event repository for database operations."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MemberEvent, MessageEvent


class EventRepository:
    """Repository for event model operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Member Events
    async def create_member_event(
        self,
        channel_id: int,
        user_id: int,
        event_type: str,
        new_status: str,
        old_status: str | None = None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        inviter_id: int | None = None,
    ) -> MemberEvent:
        """Create a new member event."""
        event = MemberEvent(
            channel_id=channel_id,
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            event_type=event_type,
            old_status=old_status,
            new_status=new_status,
            inviter_id=inviter_id,
        )
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_recent_member_events(
        self,
        channel_id: int,
        limit: int = 20,
        event_type: str | None = None,
    ) -> list[MemberEvent]:
        """Get recent member events for a channel."""
        query = (
            select(MemberEvent)
            .where(MemberEvent.channel_id == channel_id)
            .order_by(MemberEvent.created_at.desc())
            .limit(limit)
        )
        if event_type:
            query = query.where(MemberEvent.event_type == event_type)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_member_events(
        self,
        channel_id: int,
        event_type: str | None = None,
        since: datetime | None = None,
    ) -> int:
        """Count member events for a channel."""
        query = select(func.count(MemberEvent.id)).where(
            MemberEvent.channel_id == channel_id
        )
        if event_type:
            query = query.where(MemberEvent.event_type == event_type)
        if since:
            query = query.where(MemberEvent.created_at >= since)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_member_events_stats(
        self,
        channel_id: int,
        days: int = 7,
    ) -> dict[str, int]:
        """Get member events statistics; all time if days <= 0."""
        since = None
        if days > 0:
            since = datetime.now(timezone.utc) - timedelta(days=days)

        query = select(MemberEvent.event_type, func.count(MemberEvent.id)).where(
            MemberEvent.channel_id == channel_id,
        )
        if since:
            query = query.where(MemberEvent.created_at >= since)

        result = await self.session.execute(query.group_by(MemberEvent.event_type))
        return dict(result.all())

    # Message Events
    async def create_message_event(
        self,
        channel_id: int,
        user_id: int,
        message_id: int,
        event_type: str,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        content_preview: str | None = None,
    ) -> MessageEvent:
        """Create a new message event."""
        event = MessageEvent(
            channel_id=channel_id,
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            message_id=message_id,
            event_type=event_type,
            content_preview=content_preview[:500] if content_preview else None,
        )
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_recent_message_events(
        self,
        channel_id: int,
        limit: int = 20,
        event_type: str | None = None,
    ) -> list[MessageEvent]:
        """Get recent message events for a channel."""
        query = (
            select(MessageEvent)
            .where(MessageEvent.channel_id == channel_id)
            .order_by(MessageEvent.created_at.desc())
            .limit(limit)
        )
        if event_type:
            query = query.where(MessageEvent.event_type == event_type)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_message_events(
        self,
        channel_id: int,
        event_type: str | None = None,
        since: datetime | None = None,
    ) -> int:
        """Count message events for a channel."""
        query = select(func.count(MessageEvent.id)).where(
            MessageEvent.channel_id == channel_id
        )
        if event_type:
            query = query.where(MessageEvent.event_type == event_type)
        if since:
            query = query.where(MessageEvent.created_at >= since)
        result = await self.session.execute(query)
        return result.scalar() or 0
