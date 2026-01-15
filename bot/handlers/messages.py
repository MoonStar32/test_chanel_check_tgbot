"""Handler for message events (comments, etc.)."""

from loguru import logger

from aiogram import Router
from aiogram.types import Message

from database.repositories import ChannelRepository, EventRepository

router = Router(name="messages")


@router.channel_post()
async def on_channel_post(
    message: Message,
    channel_repo: ChannelRepository,
) -> None:
    """Track channel posts (optional logging)."""
    chat = message.chat

    channel = await channel_repo.get_by_id(chat.id)
    if not channel:
        return

    logger.debug(
        f"Channel post in {chat.id}: message_id={message.message_id}"
    )


@router.message()
async def on_group_message(
    message: Message,
    channel_repo: ChannelRepository,
    event_repo: EventRepository,
) -> None:
    """Track comments in linked discussion groups."""
    chat = message.chat
    user = message.from_user

    # Only process group messages
    if chat.type not in ("group", "supergroup"):
        return

    if not user or user.is_bot:
        return

    # Check if this is a linked discussion group
    # The message should have a forward_from_chat (the channel)
    # or reply_to_message with channel post
    channel_id = None

    if message.reply_to_message and message.reply_to_message.forward_from_chat:
        channel_id = message.reply_to_message.forward_from_chat.id
    elif message.reply_to_message and message.reply_to_message.sender_chat:
        channel_id = message.reply_to_message.sender_chat.id

    if not channel_id:
        return

    channel = await channel_repo.get_by_id(channel_id)
    if not channel:
        return

    # Log the comment
    content_preview = message.text[:100] if message.text else None

    await event_repo.create_message_event(
        channel_id=channel_id,
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        message_id=message.message_id,
        event_type="comment",
        content_preview=content_preview,
    )

    logger.debug(
        f"Comment tracked: user {user.id} in channel {channel_id}"
    )
