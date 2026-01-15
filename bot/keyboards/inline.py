"""Inline keyboards for the bot."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.i18n import I18n
from database.models import Channel


def get_channel_keyboard(channels: list[Channel]) -> InlineKeyboardMarkup:
    """Create keyboard with channel selection."""
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{channel.title}",
                callback_data=f"channel:{channel.id}",
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
