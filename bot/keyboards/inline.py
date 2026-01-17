"""Inline keyboards for the bot."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.i18n import I18n
from database.models import AlertSettings, Channel


def get_channel_keyboard(channels: list[Channel], prefix: str = "channel") -> InlineKeyboardMarkup:
    """Create keyboard with channel selection. Prefix allows different handlers."""
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{channel.title}",
                callback_data=f"{prefix}:{channel.id}",
            )
        ]
        for channel in channels
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_stats_period_keyboard(channel_id: int, i18n: I18n) -> InlineKeyboardMarkup:
    """Create keyboard for selecting stats period."""
    buttons = [
        [
            InlineKeyboardButton(
                text=i18n("buttons.24_hours"),
                callback_data=f"stats:{channel_id}:1",
            ),
            InlineKeyboardButton(
                text=i18n("buttons.7_days"),
                callback_data=f"stats:{channel_id}:7",
            ),
        ],
        [
            InlineKeyboardButton(
                text=i18n("buttons.30_days"),
                callback_data=f"stats:{channel_id}:30",
            ),
            InlineKeyboardButton(
                text=i18n("buttons.all_time"),
                callback_data=f"stats:{channel_id}:0",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_analytics_period_keyboard(channel_id: int, i18n: I18n) -> InlineKeyboardMarkup:
    """Create keyboard for selecting analytics period."""
    buttons = [
        [
            InlineKeyboardButton(
                text=i18n("buttons.24_hours"),
                callback_data=f"analytics:{channel_id}:1",
            ),
            InlineKeyboardButton(
                text=i18n("buttons.7_days"),
                callback_data=f"analytics:{channel_id}:7",
            ),
        ],
        [
            InlineKeyboardButton(
                text=i18n("buttons.30_days"),
                callback_data=f"analytics:{channel_id}:30",
            ),
            InlineKeyboardButton(
                text=i18n("buttons.all_time"),
                callback_data=f"analytics:{channel_id}:0",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard(i18n: I18n) -> InlineKeyboardMarkup:
    """Create back button keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=i18n("buttons.back"), callback_data="back")]
        ]
    )


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Create language selection keyboard."""
    buttons = [
        [
            InlineKeyboardButton(
                text="\U0001F1EC\U0001F1E7 English",
                callback_data="lang:en",
            ),
            InlineKeyboardButton(
                text="\U0001F1F7\U0001F1FA Русский",
                callback_data="lang:ru",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_alerts_keyboard(
    channel_id: int,
    settings: AlertSettings,
    i18n: I18n,
) -> InlineKeyboardMarkup:
    """Keyboard for tuning alert settings."""
    rows = [
        [
            InlineKeyboardButton(text="ML 3", callback_data=f"alert:mlt:{channel_id}:3"),
            InlineKeyboardButton(text="ML 5", callback_data=f"alert:mlt:{channel_id}:5"),
            InlineKeyboardButton(text="ML 10", callback_data=f"alert:mlt:{channel_id}:10"),
        ],
        [
            InlineKeyboardButton(text="Win 15m", callback_data=f"alert:mlw:{channel_id}:15"),
            InlineKeyboardButton(text="Win 30m", callback_data=f"alert:mlw:{channel_id}:30"),
            InlineKeyboardButton(text="Win 60m", callback_data=f"alert:mlw:{channel_id}:60"),
        ],
        [
            InlineKeyboardButton(text="Anom 2x", callback_data=f"alert:af:{channel_id}:2"),
            InlineKeyboardButton(text="Anom 3x", callback_data=f"alert:af:{channel_id}:3"),
            InlineKeyboardButton(text="Anom 5x", callback_data=f"alert:af:{channel_id}:5"),
        ],
        [
            InlineKeyboardButton(text="MS 100", callback_data=f"alert:ms:{channel_id}:100"),
            InlineKeyboardButton(text="MS 500", callback_data=f"alert:ms:{channel_id}:500"),
            InlineKeyboardButton(text="MS 1000", callback_data=f"alert:ms:{channel_id}:1000"),
        ],
        [
            InlineKeyboardButton(text="Churn 3%", callback_data=f"alert:ct:{channel_id}:3"),
            InlineKeyboardButton(text="Churn 5%", callback_data=f"alert:ct:{channel_id}:5"),
            InlineKeyboardButton(text="Churn 10%", callback_data=f"alert:ct:{channel_id}:10"),
        ],
        [
            InlineKeyboardButton(
                text=f"Daily {'ON' if settings.digest_daily else 'OFF'}",
                callback_data=f"alert:dd:{channel_id}:{'off' if settings.digest_daily else 'on'}",
            ),
            InlineKeyboardButton(
                text=f"Weekly {'ON' if settings.digest_weekly else 'OFF'}",
                callback_data=f"alert:wd:{channel_id}:{'off' if settings.digest_weekly else 'on'}",
            ),
            InlineKeyboardButton(
                text=f"Monthly {'ON' if settings.digest_monthly else 'OFF'}",
                callback_data=f"alert:md:{channel_id}:{'off' if settings.digest_monthly else 'on'}",
            ),
        ],
        [
            InlineKeyboardButton(text="Quiet off", callback_data=f"alert:qh:{channel_id}:0-0"),
            InlineKeyboardButton(text="Quiet 22-7", callback_data=f"alert:qh:{channel_id}:22-7"),
            InlineKeyboardButton(text="Quiet 23-8", callback_data=f"alert:qh:{channel_id}:23-8"),
        ],
        [
            InlineKeyboardButton(text=i18n("alerts.settings.clear_vips_btn"), callback_data=f"alert:vipclear:{channel_id}:0"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_export_format_keyboard(channel_id: int, i18n: I18n) -> InlineKeyboardMarkup:
    """Keyboard for choosing export format."""
    rows = [
        [
            InlineKeyboardButton(text="CSV", callback_data=f"export:{channel_id}:csv"),
            InlineKeyboardButton(text="PDF", callback_data=f"export:{channel_id}:pdf"),
            InlineKeyboardButton(text="JSON", callback_data=f"export:{channel_id}:json"),
        ],
        [
            InlineKeyboardButton(text="Sheets", callback_data=f"export:{channel_id}:sheets"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
