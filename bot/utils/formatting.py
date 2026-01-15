"""Message formatting utilities."""

from html import escape

from bot.i18n import I18n
from database.models import MemberEvent


def get_event_emoji(event_type: str) -> str:
    """Get emoji for event type."""
    emojis = {
        "join": "\u2795",  # +
        "leave": "\u2796",  # -
        "kick": "\u26d4",  # no entry
        "ban": "\U0001F6AB",  # prohibited
        "unban": "\u2705",  # check mark
        "comment": "\U0001F4AC",  # speech bubble
        "reaction": "\u2764\ufe0f",  # heart
    }
    return emojis.get(event_type, "\U0001F4CC")  # pushpin default


def format_user_link(
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    username: str | None = None,
    i18n: I18n | None = None,
) -> str:
    """Format user as HTML link."""
    if username:
        name = f"@{escape(username)}"
    else:
        parts = []
        if first_name:
            parts.append(escape(first_name))
        if last_name:
            parts.append(escape(last_name))
        if parts:
            name = " ".join(parts)
        else:
            name = i18n("common.unknown") if i18n else "Unknown"

    return f'<a href="tg://user?id={user_id}">{name}</a>'


def format_event_message(
    event: MemberEvent,
    channel_title: str,
    i18n: I18n | None = None,
) -> str:
    """Format member event notification message."""
    emoji = get_event_emoji(event.event_type)
    user_link = format_user_link(
        event.user_id,
        event.first_name,
        event.last_name,
        event.username,
        i18n,
    )

    if i18n:
        action = i18n(f"events.{event.event_type}")
    else:
        event_descriptions = {
            "join": "subscribed to",
            "leave": "left",
            "kick": "was removed from",
            "ban": "was banned in",
            "unban": "was unbanned in",
        }
        action = event_descriptions.get(event.event_type, "status changed in")

    message = f"{emoji} {user_link} {action} <b>{escape(channel_title)}</b>"

    if event.event_type == "leave":
        user_id_label = i18n("events.user_id") if i18n else "User ID:"
        message += f"\n\n<i>{user_id_label} <code>{event.user_id}</code></i>"

    return message


def format_stats_message(
    channel_title: str,
    stats: dict[str, int],
    period_days: int,
    member_counts: dict[str, int],
    i18n: I18n | None = None,
) -> str:
    """Format statistics message."""
    if i18n:
        if period_days > 0:
            period_text = i18n("stats.period_days", days=period_days)
        else:
            period_text = i18n("stats.period_all")
    else:
        period_text = f"last {period_days} days" if period_days > 0 else "all time"

    total_members = member_counts.get("member", 0)
    left_members = member_counts.get("left", 0)

    if i18n:
        message = f"{i18n('stats.title', title=escape(channel_title))}\n"
        message += f"<i>{i18n('stats.period', period=period_text)}</i>\n\n"
        message += f"{i18n('stats.current_state')}\n"
        message += f"  {i18n('stats.active_members', count=total_members)}\n"
        message += f"  {i18n('stats.left_members', count=left_members)}\n\n"
        message += f"{i18n('stats.events')}\n"
        message += f"  {get_event_emoji('join')} {i18n('stats.joins', count=stats.get('join', 0))}\n"
        message += f"  {get_event_emoji('leave')} {i18n('stats.leaves', count=stats.get('leave', 0))}\n"
        message += f"  {get_event_emoji('kick')} {i18n('stats.kicks', count=stats.get('kick', 0))}\n"
        message += f"  {get_event_emoji('ban')} {i18n('stats.bans', count=stats.get('ban', 0))}\n"
    else:
        message = f"<b>{escape(channel_title)}</b>\n"
        message += f"<i>Statistics for {period_text}</i>\n\n"
        message += "<b>Current state:</b>\n"
        message += f"  Active members: {total_members}\n"
        message += f"  Left: {left_members}\n\n"
        message += "<b>Events:</b>\n"
        message += f"  {get_event_emoji('join')} Joins: {stats.get('join', 0)}\n"
        message += f"  {get_event_emoji('leave')} Leaves: {stats.get('leave', 0)}\n"
        message += f"  {get_event_emoji('kick')} Kicks: {stats.get('kick', 0)}\n"
        message += f"  {get_event_emoji('ban')} Bans: {stats.get('ban', 0)}\n"

    net_change = stats.get("join", 0) - stats.get("leave", 0) - stats.get("kick", 0)
    trend_emoji = "\U0001F4C8" if net_change >= 0 else "\U0001F4C9"

    if i18n:
        message += f"\n{trend_emoji} {i18n('stats.net_change', change=f'{net_change:+d}')}"
    else:
        message += f"\n{trend_emoji} Net change: {net_change:+d}"

    return message
