"""Admin command handlers."""

from loguru import logger

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.i18n import I18n
from bot.keyboards import get_channel_keyboard, get_language_keyboard, get_stats_period_keyboard
from bot.services.analytics import AnalyticsService
from database.repositories import ChannelRepository, EventRepository, MemberRepository, UserRepository

router = Router(name="admin")


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    channel_repo: ChannelRepository,
    user_repo: UserRepository,
    i18n: I18n,
) -> None:
    """Handle /start command."""
    user = message.from_user
    if not user:
        return

    # Ensure user exists in DB
    await user_repo.get_or_create(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    channels = await channel_repo.get_by_admin(user.id)

    text = f"{i18n('start.title')}\n\n"
    text += f"{i18n('start.description')}\n\n"
    text += f"{i18n('start.how_to_use')}\n\n"
    text += f"{i18n('start.commands')}"

    if channels:
        text += f"\n\n<b>{i18n('start.your_channels', count=len(channels))}</b>\n"
        for ch in channels:
            status = i18n("start.channel_active") if ch.is_active else i18n("start.channel_inactive")
            text += f"  - {ch.title} ({status})\n"
    else:
        text += f"\n\n<i>{i18n('start.no_channels')}</i>"

    await message.answer(text)
    logger.info(f"User {user.id} started bot")


@router.message(Command("stats"))
async def cmd_stats(
    message: Message,
    channel_repo: ChannelRepository,
    user_repo: UserRepository,
    i18n: I18n,
) -> None:
    """Handle /stats command."""
    user = message.from_user
    if not user:
        return

    lang = await user_repo.get_language(user.id)
    local_i18n = I18n(lang)

    channels = await channel_repo.get_by_admin(user.id)

    if not channels:
        await message.answer(local_i18n("stats.no_channels"))
        return

    if len(channels) == 1:
        await message.answer(
            local_i18n("stats.select_period", title=channels[0].title),
            reply_markup=get_stats_period_keyboard(channels[0].id, local_i18n),
        )
    else:
        await message.answer(
            local_i18n("stats.select_channel"),
            reply_markup=get_channel_keyboard(channels),
        )


@router.callback_query(F.data.startswith("channel:"))
async def on_channel_select(
    callback: CallbackQuery,
    channel_repo: ChannelRepository,
    user_repo: UserRepository,
    i18n: I18n,
) -> None:
    """Handle channel selection."""
    if not callback.data:
        return

    channel_id = int(callback.data.split(":")[1])
    channel = await channel_repo.get_by_id(channel_id)

    if not channel:
        await callback.answer(i18n("stats.channel_not_found"), show_alert=True)
        return

    lang = i18n.language
    if callback.from_user:
        lang = await user_repo.get_language(callback.from_user.id)
    local_i18n = I18n(lang)

    await callback.message.edit_text(
        local_i18n("stats.select_period", title=channel.title),
        reply_markup=get_stats_period_keyboard(channel_id, local_i18n),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("stats:"))
async def on_stats_period_select(
    callback: CallbackQuery,
    channel_repo: ChannelRepository,
    member_repo: MemberRepository,
    event_repo: EventRepository,
    user_repo: UserRepository,
    i18n: I18n,
) -> None:
    """Handle stats period selection."""
    if not callback.data:
        return

    parts = callback.data.split(":")
    channel_id = int(parts[1])
    days = int(parts[2])

    channel = await channel_repo.get_by_id(channel_id)
    if not channel:
        await callback.answer(i18n("stats.channel_not_found"), show_alert=True)
        return

    # Re-resolve language to make sure we respect user's preference on callbacks
    lang = i18n.language
    if callback.from_user:
        lang = await user_repo.get_language(callback.from_user.id)
    local_i18n = I18n(lang)

    analytics = AnalyticsService(member_repo, event_repo)
    stats_message = await analytics.get_stats_message(channel, days, local_i18n)

    await callback.message.edit_text(stats_message)
    await callback.answer()


@router.message(Command("recent"))
async def cmd_recent(
    message: Message,
    channel_repo: ChannelRepository,
    member_repo: MemberRepository,
    event_repo: EventRepository,
    i18n: I18n,
) -> None:
    """Handle /recent command."""
    user = message.from_user
    if not user:
        return

    channels = await channel_repo.get_by_admin(user.id)

    if not channels:
        await message.answer(i18n("recent.no_channels"))
        return

    analytics = AnalyticsService(member_repo, event_repo)

    for channel in channels[:3]:  # Limit to 3 channels
        recent_message = await analytics.get_recent_events_message(channel, i18n=i18n)
        await message.answer(recent_message)


@router.message(Command("left"))
async def cmd_left(
    message: Message,
    channel_repo: ChannelRepository,
    member_repo: MemberRepository,
    event_repo: EventRepository,
    i18n: I18n,
) -> None:
    """Handle /left command - show who left recently."""
    user = message.from_user
    if not user:
        return

    channels = await channel_repo.get_by_admin(user.id)

    if not channels:
        await message.answer(i18n("left.no_channels"))
        return

    analytics = AnalyticsService(member_repo, event_repo)

    for channel in channels[:3]:  # Limit to 3 channels
        left_message = await analytics.get_left_members_message(channel, i18n=i18n)
        await message.answer(left_message)


@router.message(Command("export"))
async def cmd_export(
    message: Message,
    channel_repo: ChannelRepository,
    member_repo: MemberRepository,
    event_repo: EventRepository,
    i18n: I18n,
) -> None:
    """Handle /export command - export events to CSV."""
    user = message.from_user
    if not user:
        return

    channels = await channel_repo.get_by_admin(user.id)

    if not channels:
        await message.answer(i18n("export.no_channels"))
        return

    analytics = AnalyticsService(member_repo, event_repo)

    for channel in channels[:3]:
        csv_file = await analytics.export_events_csv(channel)
        await message.answer_document(
            csv_file,
            caption=i18n("export.caption", title=channel.title),
        )


@router.message(Command("setchat"))
async def cmd_setchat(
    message: Message,
    channel_repo: ChannelRepository,
    i18n: I18n,
) -> None:
    """Handle /setchat command - set notification chat."""
    user = message.from_user
    if not user:
        return

    channels = await channel_repo.get_by_admin(user.id)

    if not channels:
        await message.answer(i18n("setchat.no_channels"))
        return

    # Update notify_chat_id for all user's channels
    chat_id = message.chat.id
    updated = 0

    for channel in channels:
        await channel_repo.set_notify_chat(channel.id, chat_id)
        updated += 1

    await message.answer(i18n("setchat.success", count=updated))


@router.message(Command("language"))
async def cmd_language(
    message: Message,
    i18n: I18n,
) -> None:
    """Handle /language command - show language selection."""
    await message.answer(
        i18n("language.select"),
        reply_markup=get_language_keyboard(),
    )


@router.callback_query(F.data.startswith("lang:"))
async def on_language_select(
    callback: CallbackQuery,
    user_repo: UserRepository,
) -> None:
    """Handle language selection."""
    if not callback.data or not callback.from_user:
        return

    language = callback.data.split(":")[1]

    # Ensure user exists
    await user_repo.get_or_create(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
        language=language,
    )

    # Update language
    await user_repo.set_language(callback.from_user.id, language)

    # Get new i18n instance for confirmation message
    new_i18n = I18n(language)

    await callback.message.edit_text(new_i18n("language.changed"))
    await callback.answer()

    logger.info(f"User {callback.from_user.id} changed language to {language}")


@router.message(Command("help"))
async def cmd_help(
    message: Message,
    i18n: I18n,
) -> None:
    """Handle /help command."""
    text = f"{i18n('help.title')}\n\n"
    text += f"{i18n('help.setup')}\n\n"
    text += f"{i18n('help.commands')}\n\n"
    text += i18n("help.tracked_events")

    await message.answer(text)
