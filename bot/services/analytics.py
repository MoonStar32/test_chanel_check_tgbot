"""Analytics service for generating reports."""

import csv
import io
from datetime import datetime, timedelta, timezone
from statistics import mean

from aiogram.types import BufferedInputFile

from bot.i18n import I18n
from bot.utils.formatting import format_stats_message, format_user_link, get_event_emoji
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

    async def get_growth_dynamics_message(
        self,
        channel: Channel,
        days: int = 30,
        i18n: I18n | None = None,
    ) -> str:
        """Build growth dynamics message: daily flow, churn/net/forecast."""
        stats = await self.event_repo.get_member_events_stats(channel.id, days)
        flow = await self.event_repo.get_daily_member_flow(channel.id, days)
        member_counts = await self.member_repo.count_by_status(channel.id)

        joins = stats.get("join", 0)
        leaves = stats.get("leave", 0) + stats.get("kick", 0)
        net = joins - leaves

        active_members = member_counts.get("member", 0)
        total_population = active_members + member_counts.get("left", 0)
        churn_rate = (leaves / total_population * 100) if total_population > 0 else 0.0
        retention_rate = 100 - churn_rate

        net_per_day = [day["net"] for day in flow] or [0]
        avg_net = mean(net_per_day)
        forecast_7d = int(round(avg_net * 7))

        lines = []
        if i18n:
            lines.append(i18n("analytics.growth.title", title=channel.title))
            lines.append(
                i18n(
                    "analytics.growth.summary",
                    joins=joins,
                    leaves=leaves,
                    net=f"{net:+d}",
                )
            )
            lines.append(
                i18n(
                    "analytics.growth.churn_retention",
                    churn=f"{churn_rate:.1f}%",
                    retention=f"{retention_rate:.1f}%",
                )
            )
            lines.append(
                i18n(
                    "analytics.growth.forecast",
                    forecast=f"{forecast_7d:+d}",
                    avg=f"{avg_net:.1f}",
                )
            )
        else:
            lines.append(f"<b>Growth for {channel.title}</b>")
            lines.append(f"Joins: {joins}, Leaves: {leaves}, Net: {net:+d}")
            lines.append(f"Churn: {churn_rate:.1f}%, Retention: {retention_rate:.1f}%")
            lines.append(f"Forecast 7d net: {forecast_7d:+d} (avg/day {avg_net:.1f})")

        if flow:
            lines.append("")
            if i18n:
                lines.append(i18n("analytics.growth.trend_header"))
            else:
                lines.append("Trend by day:")

            for day in flow[-10:]:
                date_str = day["day"].strftime("%d.%m")
                lines.append(
                    f"{date_str}: +{day['join']} / -{day['leave']} / net {day['net']:+d}"
                )

        return "\n".join(lines)

    async def get_activity_insights_message(
        self,
        channel: Channel,
        days: int = 30,
        i18n: I18n | None = None,
    ) -> str:
        """Build time-of-day/day-of-week insights."""
        activity = await self.event_repo.get_hourly_activity(channel.id, days)

        if not activity:
            return i18n("analytics.activity.no_data") if i18n else "No activity data."

        # Top hours by joins
        top_hours = sorted(activity, key=lambda x: x["joins"], reverse=True)[:5]

        # Aggregate by dow
        dow_totals: dict[int, int] = {}
        for row in activity:
            dow_totals[row["dow"]] = dow_totals.get(row["dow"], 0) + row["joins"]
        top_days = sorted(dow_totals.items(), key=lambda x: x[1], reverse=True)[:3]

        lines = []
        if i18n:
            lines.append(i18n("analytics.activity.title", title=channel.title))
            lines.append(i18n("analytics.activity.best_hours"))
            for row in top_hours:
                lines.append(
                    i18n(
                        "analytics.activity.hour_line",
                        hour=row["hour"],
                        joins=row["joins"],
                        net=f"{row['net']:+d}",
                    )
                )
            lines.append("")
            lines.append(i18n("analytics.activity.best_days"))
            for dow, joins in top_days:
                lines.append(
                    i18n(
                        "analytics.activity.day_line",
                        dow=dow,
                        joins=joins,
                    )
                )
        else:
            lines.append(f"<b>Activity for {channel.title}</b>")
            lines.append("Top hours:")
            for row in top_hours:
                lines.append(
                    f"  {row['hour']:02d}:00 — joins {row['joins']} (net {row['net']:+d})"
                )
            lines.append("Top days:")
            for dow, joins in top_days:
                lines.append(f"  DOW {dow}: joins {joins}")

        return "\n".join(lines)

    async def get_audience_insights_message(
        self,
        channel: Channel,
        days: int = 60,
        i18n: I18n | None = None,
    ) -> str:
        """Audience-focused analytics: sources, churners, returnees, ghosts."""
        top_sources = await self.event_repo.get_top_inviter_sources(channel.id, days)
        top_leavers = await self.event_repo.get_top_leavers(channel.id, days)
        returnees = await self.event_repo.get_returnees(channel.id, days)
        ghosts = await self.event_repo.get_inactive_members(channel.id, inactive_days=30)

        lines = []
        if i18n:
            lines.append(i18n("analytics.audience.title", title=channel.title))
        else:
            lines.append(f"<b>Audience insights for {channel.title}</b>")

        # Sources
        if i18n:
            lines.append(i18n("analytics.audience.sources"))
        else:
            lines.append("Sources:")
        if top_sources:
            for inviter_id, count in top_sources:
                inviter = format_user_link(inviter_id, i18n=i18n)
                lines.append(f"  {inviter}: {count}")
        else:
            lines.append(f"  {i18n('analytics.audience.no_sources') if i18n else 'No inviter data'}")

        # Top leavers
        lines.append("")
        if i18n:
            lines.append(i18n("analytics.audience.leavers"))
        else:
            lines.append("Top leavers:")
        if top_leavers:
            for row in top_leavers:
                user = format_user_link(
                    row["user_id"],
                    row.get("first_name"),
                    row.get("last_name"),
                    row.get("username"),
                    i18n,
                )
                lines.append(f"  {user}: {row['leaves']} leave(s)")
        else:
            lines.append(f"  {i18n('analytics.audience.no_leavers') if i18n else 'No leaves'}")

        # Returnees
        lines.append("")
        if i18n:
            lines.append(i18n("analytics.audience.returnees"))
        else:
            lines.append("Returnees:")
        if returnees:
            for row in returnees:
                user = format_user_link(
                    row["user_id"],
                    row.get("first_name"),
                    row.get("last_name"),
                    row.get("username"),
                    i18n,
                )
                lines.append(f"  {user}: +{row['joins']} / -{row['leaves']}")
        else:
            lines.append(f"  {i18n('analytics.audience.no_returnees') if i18n else 'No returnees'}")

        # Ghosts
        lines.append("")
        if i18n:
            lines.append(i18n("analytics.audience.ghosts"))
        else:
            lines.append("Inactive members:")
        if ghosts:
            for row in ghosts:
                user = format_user_link(
                    row["user_id"],
                    row.get("first_name"),
                    row.get("last_name"),
                    row.get("username"),
                    i18n,
                )
                joined = row["joined_at"].strftime("%d.%m") if row.get("joined_at") else "-"
                lines.append(f"  {user}: joined {joined}")
        else:
            lines.append(f"  {i18n('analytics.audience.no_ghosts') if i18n else 'No inactive members'}")

        return "\n".join(lines)
