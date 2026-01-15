"""Handler for channel member updates - the core feature."""

from loguru import logger

from aiogram import Bot, Router
from aiogram.types import ChatMemberUpdated

from bot.i18n import I18n
from bot.services.notifications import NotificationService
from database.repositories import ChannelRepository, EventRepository, MemberRepository, UserRepository

router = Router(name="channel_events")


def get_member_status(member) -> str:
    """Extract status from ChatMember object."""
    status = member.status
    if status in ("creator", "administrator", "member", "restricted"):
        return "member"
    return status  # left, kicked, banned


def get_event_type(old_status: str, new_status: str) -> str:
    """Determine event type based on status change."""
    if new_status == "member" and old_status in ("left", "kicked", "banned"):
        return "join"
    if new_status == "left":
        return "leave"
    if new_status == "kicked":
        return "kick"
    if new_status == "banned":
        return "ban"
    if old_status == "banned" and new_status in ("left", "member"):
        return "unban"
    return "status_change"


@router.chat_member()
async def on_chat_member_update(
    event: ChatMemberUpdated,
    bot: Bot,
    channel_repo: ChannelRepository,
    member_repo: MemberRepository,
    event_repo: EventRepository,
    user_repo: UserRepository,
) -> None:
    """Handle channel member status updates."""
    chat = event.chat
    user = event.new_chat_member.user

    # Only process channel events
    if chat.type != "channel":
        return

    # Skip bot's own status changes
    if user.is_bot:
        return

    old_status = get_member_status(event.old_chat_member)
    new_status = get_member_status(event.new_chat_member)

    # Skip if status didn't change
    if old_status == new_status:
        return

    event_type = get_event_type(old_status, new_status)

    logger.info(
        f"Channel {chat.id} ({chat.title}): User {user.id} "
        f"({user.username or user.first_name}) - {event_type} "
        f"({old_status} -> {new_status})"
    )

    # Get or create channel
    channel = await channel_repo.get_by_id(chat.id)
    if not channel:
        logger.warning(f"Channel {chat.id} not registered, skipping event")
        return

    # Update member status
    await member_repo.upsert(
        channel_id=chat.id,
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        status=new_status,
    )

    # Get inviter if available
    inviter_id = None
    if event.invite_link and event.invite_link.creator:
        inviter_id = event.invite_link.creator.id
    elif event.from_user and event.from_user.id != user.id:
        inviter_id = event.from_user.id

    # Create event record
    member_event = await event_repo.create_member_event(
        channel_id=chat.id,
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        event_type=event_type,
        old_status=old_status,
        new_status=new_status,
        inviter_id=inviter_id,
    )

    # Send notification with admin's language preference
    admin_lang = await user_repo.get_language(channel.admin_user_id)
    i18n = I18n(admin_lang)
    notification_service = NotificationService(bot, i18n)
    await notification_service.notify_member_event(member_event, channel)


@router.my_chat_member()
async def on_bot_added_to_channel(
    event: ChatMemberUpdated,
    bot: Bot,
    channel_repo: ChannelRepository,
    user_repo: UserRepository,
) -> None:
    """Handle bot being added to or removed from a channel."""
    chat = event.chat

    # Only process channel events
    if chat.type != "channel":
        return

    old_status = get_member_status(event.old_chat_member)
    new_status = get_member_status(event.new_chat_member)

    # Bot was added to channel
    if new_status == "member" and old_status in ("left", "kicked", "banned"):
        admin_id = event.from_user.id if event.from_user else 0

        channel, created = await channel_repo.get_or_create(
            channel_id=chat.id,
            title=chat.title or "Unknown",
            admin_user_id=admin_id,
            username=chat.username,
        )

        # Set notification chat to the admin who added the bot
        if created and admin_id:
            await channel_repo.set_notify_chat(chat.id, admin_id)

            # Send welcome message to admin with their language preference
            admin_lang = await user_repo.get_language(admin_id)
            i18n = I18n(admin_lang)
            notification_service = NotificationService(bot, i18n)
            await notification_service.send_welcome(admin_id, channel)

        logger.info(
            f"Bot added to channel {chat.id} ({chat.title}) by user {admin_id}"
        )

    # Bot was removed from channel
    elif new_status in ("left", "kicked", "banned"):
        await channel_repo.deactivate(chat.id)
        logger.info(f"Bot removed from channel {chat.id} ({chat.title})")
