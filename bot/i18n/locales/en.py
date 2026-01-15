"""English locale."""

LOCALE = {
    "language": {
        "name": "English",
        "flag": "\U0001F1EC\U0001F1E7",
        "select": "Select language:",
        "changed": "Language changed to English",
    },
    "start": {
        "title": "<b>Channel Analytics Bot</b>",
        "description": (
            "I track channel subscriber activity:\n"
            "  - New subscriptions\n"
            "  - Unsubscriptions\n"
            "  - Kicks and bans\n"
            "  - Comments (in linked groups)"
        ),
        "how_to_use": (
            "<b>How to use:</b>\n"
            "1. Add me to your channel as administrator\n"
            "2. Give me permission to see channel members\n"
            "3. I'll send you notifications about all events"
        ),
        "commands": (
            "<b>Commands:</b>\n"
            "/stats - View channel statistics\n"
            "/recent - Recent events\n"
            "/left - Who left recently\n"
            "/export - Export to CSV\n"
            "/setchat - Set notification chat\n"
            "/language - Change language"
        ),
        "your_channels": "Your channels ({count}):",
        "no_channels": "No channels yet. Add me to a channel to start!",
        "channel_active": "active",
        "channel_inactive": "inactive",
    },
    "stats": {
        "select_channel": "Select a channel:",
        "select_period": "Select period for <b>{title}</b>:",
        "no_channels": (
            "You don't have any channels yet.\n"
            "Add me to a channel as administrator first!"
        ),
        "channel_not_found": "Channel not found",
        "title": "<b>{title}</b>",
        "period": "Statistics for {period}",
        "period_days": "last {days} days",
        "period_all": "all time",
        "current_state": "<b>Current state:</b>",
        "active_members": "Active members: {count}",
        "left_members": "Left: {count}",
        "events": "<b>Events:</b>",
        "joins": "Joins: {count}",
        "leaves": "Leaves: {count}",
        "kicks": "Kicks: {count}",
        "bans": "Bans: {count}",
        "net_change": "Net change: {change}",
    },
    "recent": {
        "title": "<b>Recent events in {title}:</b>",
        "no_events": "No recent events for <b>{title}</b>",
        "no_channels": "You don't have any channels yet.",
    },
    "left": {
        "title": "<b>Left {title} (last {days} days):</b>",
        "no_one_left": "No one left <b>{title}</b> in the last {days} days",
        "total": "Total: {count}",
        "no_channels": "You don't have any channels yet.",
    },
    "export": {
        "caption": "Events export for {title}",
        "no_channels": "You don't have any channels yet.",
    },
    "setchat": {
        "success": "Notifications for {count} channel(s) will be sent to this chat.",
        "no_channels": "You don't have any channels yet.",
    },
    "help": {
        "title": "<b>Channel Analytics Bot - Help</b>",
        "setup": (
            "<b>Setup:</b>\n"
            "1. Add bot to your channel as admin\n"
            "2. Grant 'See members' permission\n"
            "3. Bot will auto-register the channel"
        ),
        "commands": (
            "<b>Commands:</b>\n"
            "/start - Welcome message and channel list\n"
            "/stats - Channel statistics\n"
            "/recent - Recent member events\n"
            "/left - Who left the channel\n"
            "/export - Export events to CSV\n"
            "/setchat - Set where to receive notifications\n"
            "/language - Change language\n"
            "/help - This message"
        ),
        "tracked_events": (
            "<b>Tracked events:</b>\n"
            "  - New subscribers\n"
            "  - Unsubscribes (the main feature!)\n"
            "  - Kicks and bans\n"
            "  - Comments in linked groups"
        ),
    },
    "welcome": {
        "added": "Bot has been added to <b>{title}</b>!",
        "tracking": (
            "I will track all member activity:\n"
            "  - New subscribers\n"
            "  - Unsubscribes\n"
            "  - Kicks and bans"
        ),
        "notifications": "Notifications will be sent here.",
        "commands": (
            "Use /stats to view statistics.\n"
            "Use /recent to see recent events."
        ),
    },
    "events": {
        "join": "subscribed to",
        "leave": "left",
        "kick": "was removed from",
        "ban": "was banned in",
        "unban": "was unbanned in",
        "status_change": "status changed in",
        "user_id": "User ID:",
    },
    "buttons": {
        "24_hours": "24 hours",
        "7_days": "7 days",
        "30_days": "30 days",
        "all_time": "All time",
        "back": "Back",
    },
    "common": {
        "unknown": "Unknown",
    },
}
