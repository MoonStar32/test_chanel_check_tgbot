"""Notification service for sending alerts."""

from loguru import logger

from aiogram import Bot

from bot.i18n import I18n
from bot.utils.formatting import format_event_message
from database.models import Channel, MemberEvent


class NotificationService:
    """Service for sending notifications to channel admins."""

    def __init__(self, bot: Bot, i18n: I18n | None = None) -> None:
        self.bot = bot
        self.i18n = i18n

    async def send_text(self, chat_id: int, text: str) -> bool:
        """Send a plain text message."""
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                disable_web_page_preview=True,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send text notification: {e}")
            return False

    async def notify_member_event(
        self,
        event: MemberEvent,
        channel: Channel,
    ) -> bool:
        """Send notification about member event."""
        if not channel.notify_chat_id:
            logger.warning(
                f"No notify_chat_id for channel {channel.id}, skipping notification"
            )
            return False

        message = format_event_message(event, channel.title, self.i18n)

        try:
            await self.bot.send_message(
                chat_id=channel.notify_chat_id,
                text=message,
                disable_web_page_preview=True,
            )
            logger.info(
                f"Sent {event.event_type} notification for user {event.user_id} "
                f"in channel {channel.id}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    async def send_welcome(
        self,
        chat_id: int,
        channel: Channel,
    ) -> bool:
        """Send welcome message when bot is added to channel."""
        if self.i18n:
            message = f"{self.i18n('welcome.added', title=channel.title)}\n\n"
            message += f"{self.i18n('welcome.tracking')}\n\n"
            message += f"{self.i18n('welcome.notifications')}\n\n"
            message += self.i18n("welcome.commands")
        else:
            message = (
                f"Bot has been added to <b>{channel.title}</b>!\n\n"
                f"I will track all member activity:\n"
                f"  - New subscribers\n"
                f"  - Unsubscribes\n"
                f"  - Kicks and bans\n\n"
                f"Notifications will be sent here.\n\n"
                f"Use /stats to view statistics.\n"
                f"Use /recent to see recent events."
            )

        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")
            return False
