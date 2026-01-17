"""Event repository for database operations."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Member, MemberEvent, MessageEvent


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

    async def get_daily_member_flow(
        self,
        channel_id: int,
        days: int = 30,
    ) -> list[dict[str, object]]:
        """Aggregate joins/leaves per day for the given window. Returns ordered list of dicts."""
        since = None
        if days > 0:
            since = datetime.now(timezone.utc) - timedelta(days=days)

        day_col = func.date_trunc("day", MemberEvent.created_at).label("day")
        query = (
            select(day_col, MemberEvent.event_type, func.count(MemberEvent.id))
            .where(MemberEvent.channel_id == channel_id)
            .group_by(day_col, MemberEvent.event_type)
            .order_by(day_col)
        )
        if since:
            query = query.where(MemberEvent.created_at >= since)

        result = await self.session.execute(query)
        rows = result.all()

        by_day: dict[datetime, dict[str, int]] = {}
        for day, event_type, count in rows:
            by_day.setdefault(day, {"join": 0, "leave": 0, "kick": 0, "ban": 0})[
                event_type
            ] = count

        flow = []
        for day in sorted(by_day.keys()):
            counts = by_day[day]
            net = counts.get("join", 0) - counts.get("leave", 0) - counts.get("kick", 0)
            flow.append(
                {
                    "day": day,
                    "join": counts.get("join", 0),
                    "leave": counts.get("leave", 0),
                    "kick": counts.get("kick", 0),
                    "ban": counts.get("ban", 0),
                    "net": net,
                }
            )
        return flow

    async def get_hourly_activity(
        self,
        channel_id: int,
        days: int = 30,
    ) -> list[dict[str, int | float]]:
        """Aggregate activity by day-of-week and hour."""
        since = None
        if days > 0:
            since = datetime.now(timezone.utc) - timedelta(days=days)

        dow_col = func.extract("dow", MemberEvent.created_at).label("dow")
        hour_col = func.extract("hour", MemberEvent.created_at).label("hour")
        query = (
            select(
                dow_col,
                hour_col,
                func.count(MemberEvent.id).label("events"),
                func.sum(
                    case(
                        (MemberEvent.event_type == "join", 1),
                        else_=0,
                    )
                ).label("joins"),
                func.sum(
                    case(
                        (MemberEvent.event_type.in_(["leave", "kick", "ban"]), 1),
                        else_=0,
                    )
                ).label("leaves"),
            )
            .where(MemberEvent.channel_id == channel_id)
            .group_by(dow_col, hour_col)
            .order_by(dow_col, hour_col)
        )
        if since:
            query = query.where(MemberEvent.created_at >= since)

        result = await self.session.execute(query)
        rows = result.all()

        activity = []
        for dow, hour, events, joins, leaves in rows:
            net = (joins or 0) - (leaves or 0)
            activity.append(
                {
                    "dow": int(dow),
                    "hour": int(hour),
                    "events": int(events),
                    "joins": int(joins or 0),
                    "leaves": int(leaves or 0),
                    "net": int(net),
                }
            )
        return activity

    async def get_top_inviter_sources(
        self,
        channel_id: int,
        days: int = 30,
        limit: int = 5,
    ) -> list[tuple[int | None, int]]:
        """Top inviters (by inviter_id) over the window."""
        since = None
        if days > 0:
            since = datetime.now(timezone.utc) - timedelta(days=days)

        query = select(MemberEvent.inviter_id, func.count(MemberEvent.id)).where(
            MemberEvent.channel_id == channel_id,
            MemberEvent.event_type == "join",
        )
        if since:
            query = query.where(MemberEvent.created_at >= since)

        query = (
            query.group_by(MemberEvent.inviter_id)
            .order_by(func.count(MemberEvent.id).desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [(row[0], row[1]) for row in result.all() if row[0] is not None]

    async def get_top_leavers(
        self,
        channel_id: int,
        days: int = 60,
        limit: int = 5,
    ) -> list[dict[str, object]]:
        """Users who left most often within the window."""
        since = None
        if days > 0:
            since = datetime.now(timezone.utc) - timedelta(days=days)

        base = select(
            MemberEvent.user_id,
            func.count(MemberEvent.id).label("leaves"),
            func.max(MemberEvent.username).label("username"),
            func.max(MemberEvent.first_name).label("first_name"),
            func.max(MemberEvent.last_name).label("last_name"),
        ).where(MemberEvent.channel_id == channel_id, MemberEvent.event_type == "leave")

        if since:
            base = base.where(MemberEvent.created_at >= since)

        query = base.group_by(MemberEvent.user_id).order_by(func.count(MemberEvent.id).desc()).limit(limit)
        result = await self.session.execute(query)

        output = []
        for user_id, leaves, username, first_name, last_name in result.all():
            output.append(
                {
                    "user_id": user_id,
                    "leaves": leaves,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                }
            )
        return output

    async def get_returnees(
        self,
        channel_id: int,
        days: int = 60,
        limit: int = 5,
    ) -> list[dict[str, object]]:
        """Users who left and returned within the window."""
        since = None
        if days > 0:
            since = datetime.now(timezone.utc) - timedelta(days=days)

        base = select(
            MemberEvent.user_id,
            func.max(MemberEvent.username).label("username"),
            func.max(MemberEvent.first_name).label("first_name"),
            func.max(MemberEvent.last_name).label("last_name"),
            func.count(
                case((MemberEvent.event_type == "join", 1))
            ).label("joins"),
            func.count(
                case((MemberEvent.event_type == "leave", 1))
            ).label("leaves"),
        ).where(MemberEvent.channel_id == channel_id)

        if since:
            base = base.where(MemberEvent.created_at >= since)

        query = (
            base.group_by(MemberEvent.user_id)
            .having(func.count(case((MemberEvent.event_type == "join", 1))) > 0)
            .having(func.count(case((MemberEvent.event_type == "leave", 1))) > 0)
            .order_by(func.count(case((MemberEvent.event_type == "join", 1))).desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        output = []
        for user_id, username, first_name, last_name, joins, leaves in result.all():
            output.append(
                {
                    "user_id": user_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "joins": joins,
                    "leaves": leaves,
                }
            )
        return output

    async def get_inactive_members(
        self,
        channel_id: int,
        inactive_days: int = 30,
        limit: int = 5,
    ) -> list[dict[str, object]]:
        """Members with no recent events (simple heuristic for 'ghosts')."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=inactive_days)

        last_event_sub = (
            select(
                MemberEvent.user_id,
                func.max(MemberEvent.created_at).label("last_event_at"),
            )
            .where(MemberEvent.channel_id == channel_id)
            .group_by(MemberEvent.user_id)
            .subquery()
        )

        query = (
            select(
                Member.user_id,
                Member.username,
                Member.first_name,
                Member.last_name,
                Member.joined_at,
                last_event_sub.c.last_event_at,
            )
            .outerjoin(last_event_sub, last_event_sub.c.user_id == Member.user_id)
            .where(
                Member.channel_id == channel_id,
                Member.status == "member",
                Member.joined_at <= cutoff,
                func.coalesce(last_event_sub.c.last_event_at, Member.joined_at)
                <= cutoff,
            )
            .order_by(Member.joined_at)
            .limit(limit)
        )

        result = await self.session.execute(query)
        ghosts = []
        for user_id, username, first_name, last_name, joined_at, last_event_at in result.all():
            ghosts.append(
                {
                    "user_id": user_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "joined_at": joined_at,
                    "last_event_at": last_event_at,
                }
            )
        return ghosts

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
