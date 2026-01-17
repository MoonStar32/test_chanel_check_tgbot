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
            "/analytics - Advanced analytics\n"
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
        "select_channel": "Select a channel to export:",
        "select_format": "Select export format for <b>{title}</b>:",
        "channel_not_found": "Channel not found",
        "caption_pdf": "PDF report for {title}",
        "caption_json": "JSON export for {title}",
        "sheets_success": "Exported to Google Sheets for {title}",
        "sheets_fail": "Google Sheets export not configured.",
        "creds_set": "Google credentials saved.",
        "sheet_set": "Spreadsheet ID saved.",
        "cleared": "Google export settings cleared.",
        "need_creds": "Set credentials and spreadsheet via /sheets.",
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
            "/analytics - Advanced analytics\n"
            "/alerts - Configure alerts\n"
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
        "analytics": {
        "common": {
            "select_channel": "Select a channel for analytics:",
            "select_period": "Select period for <b>{title}</b>:",
            "no_channels": "You don't have any channels yet.",
            "channel_not_found": "Channel not found",
        },
        "growth": {
            "title": "<b>Growth for {title}</b>",
            "summary": "Joins: {joins}, Leaves: {leaves}, Net: {net}",
            "churn_retention": "Churn: {churn}, Retention: {retention}",
            "forecast": "Forecast 7d net: {forecast} (avg/day {avg})",
            "trend_header": "Trend by day (last 10):",
        },
        "activity": {
            "title": "<b>Activity for {title}</b>",
            "best_hours": "<b>Top hours (UTC):</b>",
            "hour_line": "  {hour:02d}:00 — joins {joins} (net {net})",
            "best_days": "<b>Top days of week (0=Sun):</b>",
            "day_line": "  {dow} — joins {joins}",
            "no_data": "No activity data yet.",
        },
        "audience": {
            "title": "<b>Audience insights for {title}</b>",
            "sources": "<b>Top inviters:</b>",
            "no_sources": "No inviter data.",
            "leavers": "<b>Top leavers:</b>",
            "no_leavers": "No leaves.",
            "returnees": "<b>Returnees:</b>",
            "no_returnees": "No returnees yet.",
            "ghosts": "<b>Inactive members (30+ days):</b>",
            "no_ghosts": "No inactive members.",
        },
    },
        "alerts": {
        "mass_leave": "\u26a0\ufe0f Mass unsubscribes in <b>{title}</b>: {count} in last {minutes} min",
        "anomaly_spike": "\u26a0\ufe0f Spike detected in <b>{title}</b>: {count} events in last hour",
        "anomaly_drop": "\u26a0\ufe0f Activity drop detected in <b>{title}</b>",
        "milestone": "\ud83c\udf89 Milestone in <b>{title}</b>: {milestone} members!",
        "churn_threshold": "\u26a0\ufe0f Churn alert in <b>{title}</b>: {churn} (threshold {threshold})",
        "vip_left": "\ud83d\udd25 VIP left <b>{title}</b> (ID {user_id})",
        "digest_daily_prefix": "\ud83d\udcc5 Daily digest",
        "digest_weekly_prefix": "\ud83d\udcca Weekly digest",
        "digest_monthly_prefix": "\ud83d\udccb Monthly digest",
        "settings": {
            "title": "<b>Alert settings for {title}</b>",
            "mass_leave": "Mass leave: {count} in {minutes}m",
            "anomaly": "Anomaly factor: {factor}x",
            "milestone": "Milestone step: {step} (last {last})",
            "churn": "Churn alert threshold: {threshold}",
            "daily": "Daily digest: {state}",
            "weekly": "Weekly digest: {state}",
            "monthly": "Monthly digest: {state}",
            "quiet": "Quiet hours: {quiet}",
            "quiet_off": "off",
            "vips": "VIP IDs: {vips}",
            "vips_none": "none",
            "clear_vips_btn": "Clear VIPs",
            "updated": "Settings updated",
            "no_channels": "You don't have any channels yet.",
            "select_channel": "Select a channel to configure alerts:",
            "channel_not_found": "Channel not found",
            "vip_usage": "Use: /vip_add <id1> <id2> ...",
            "vips_set": "VIP list set: {vips}",
            "vips_cleared": "VIP list cleared",
            "on": "ON",
            "off": "OFF",
        },
    },
}
