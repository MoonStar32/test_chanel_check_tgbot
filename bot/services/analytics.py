"""Analytics service for generating reports."""

import csv
import io
from datetime import datetime, timedelta, timezone

from aiogram.types import BufferedInputFile

from bot.i18n import I18n
from bot.utils.formatting import format_stats_message, get_event_emoji
from database.models import Channel
from database.repositories import EventRepository, MemberRepository


class AnalyticsService:
    """Service for generating analytics and reports."""

    def __init__(
        self,
        member_repo: MemberRepository,
        event_repo: EventRepository,
    ) -> None:
        self.member_repo = member_repo
        self.event_repo = event_repo

    async def get_stats_message(
        self,
        channel: Channel,
        days: int = 7,
        i18n: I18n | None = None,
    ) -> str:
        """Get formatted statistics message."""
        stats = await self.event_repo.get_member_events_stats(channel.id, days)
        member_counts = await self.member_repo.count_by_status(channel.id)

        return format_stats_message(
            channel_title=channel.title,
            stats=stats,
            period_days=days,
            member_counts=member_counts,
            i18n=i18n,
        )

    async def get_recent_events_message(
        self,
        channel: Channel,
        limit: int = 10,
        i18n: I18n | None = None,
    ) -> str:
        """Get formatted recent events message."""
        events = await self.event_repo.get_recent_member_events(channel.id, limit)

        if not events:
            if i18n:
                return i18n("recent.no_events", title=channel.title)
            return f"No recent events for <b>{channel.title}</b>"

        if i18n:
            lines = [f"{i18n('recent.title', title=channel.title)}\n"]
        else:
            lines = [f"<b>Recent events in {channel.title}:</b>\n"]

        for event in events:
            emoji = get_event_emoji(event.event_type)
            name = event.mention
            time_str = event.created_at.strftime("%d.%m %H:%M")
            if i18n:
                event_label = i18n(f"events.{event.event_type}")
            else:
                event_label = event.event_type

            lines.append(f"{emoji} {name} - {event_label} ({time_str})")

        return "\n".join(lines)

    async def export_events_csv(
        self,
        channel: Channel,
        days: int = 30,
    ) -> BufferedInputFile:
        """Export events to CSV file."""
        now = datetime.now(timezone.utc)
        since = now - timedelta(days=days) if days > 0 else None
        events = await self.event_repo.get_recent_member_events(
            channel.id,
            limit=10000,
        )

        if since:
            events = [e for e in events if e.created_at >= since]

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Date",
            "Time",
            "Event Type",
            "User ID",
            "Username",
            "First Name",
            "Last Name",
            "Old Status",
            "New Status",
        ])

        for event in events:
            writer.writerow([
                event.created_at.strftime("%Y-%m-%d"),
                event.created_at.strftime("%H:%M:%S"),
                event.event_type,
                event.user_id,
                event.username or "",
                event.first_name or "",
                event.last_name or "",
                event.old_status or "",
                event.new_status,
            ])

        csv_bytes = output.getvalue().encode("utf-8")
        filename = f"events_{channel.id}_{now.strftime('%Y%m%d')}.csv"

        return BufferedInputFile(csv_bytes, filename=filename)

    async def get_left_members_message(
        self,
        channel: Channel,
        days: int = 7,
        i18n: I18n | None = None,
    ) -> str:
        """Get list of members who left recently."""
        events = await self.event_repo.get_recent_member_events(
            channel.id,
            limit=50,
            event_type="leave",
        )

        since = datetime.now(timezone.utc) - timedelta(days=days)
        recent_events = [e for e in events if e.created_at >= since]

        if not recent_events:
            if i18n:
                return i18n("left.no_one_left", title=channel.title, days=days)
            return f"No one left <b>{channel.title}</b> in the last {days} days"

        if i18n:
            lines = [f"{i18n('left.title', title=channel.title, days=days)}\n"]
        else:
            lines = [f"<b>Left {channel.title} (last {days} days):</b>\n"]

        for event in recent_events:
            name = event.mention
            time_str = event.created_at.strftime("%d.%m %H:%M")
            lines.append(f"  {get_event_emoji('leave')} {name} ({time_str})")

        if i18n:
            lines.append(f"\n<i>{i18n('left.total', count=len(recent_events))}</i>")
        else:
            lines.append(f"\n<i>Total: {len(recent_events)}</i>")

        return "\n".join(lines)
