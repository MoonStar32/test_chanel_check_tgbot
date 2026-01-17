"""Admin command handlers."""

from loguru import logger

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.i18n import I18n
from bot.keyboards import (
    get_alerts_keyboard,
    get_analytics_period_keyboard,
    get_channel_keyboard,
    get_export_format_keyboard,
    get_language_keyboard,
    get_stats_period_keyboard,
)
from bot.services.analytics import AnalyticsService
from bot.services.reports import ReportsService
from bot.utils.alerts import format_alerts_summary
from database.repositories import (
    AlertSettingsRepository,
    ChannelRepository,
    EventRepository,
    GoogleSettingsRepository,
    MemberRepository,
    UserRepository,
)

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


@router.message(Command("analytics"))
async def cmd_analytics(
    message: Message,
    channel_repo: ChannelRepository,
    user_repo: UserRepository,
    i18n: I18n,
) -> None:
    """Handle /analytics command."""
    user = message.from_user
    if not user:
        return

    lang = await user_repo.get_language(user.id)
    local_i18n = I18n(lang)

    channels = await channel_repo.get_by_admin(user.id)

    if not channels:
        await message.answer(local_i18n("analytics.common.no_channels"))
        return

    if len(channels) == 1:
        await message.answer(
            local_i18n("analytics.common.select_period", title=channels[0].title),
            reply_markup=get_analytics_period_keyboard(channels[0].id, local_i18n),
        )
    else:
        await message.answer(
            local_i18n("analytics.common.select_channel"),
            reply_markup=get_channel_keyboard(channels, prefix="achannel"),
        )


@router.callback_query(F.data.startswith("achannel:"))
async def on_analytics_channel_select(
    callback: CallbackQuery,
    channel_repo: ChannelRepository,
    user_repo: UserRepository,
    i18n: I18n,
) -> None:
    """Select channel for analytics."""
    if not callback.data:
        return

    channel_id = int(callback.data.split(":")[1])
    channel = await channel_repo.get_by_id(channel_id)

    if not channel:
        await callback.answer(i18n("analytics.common.channel_not_found"), show_alert=True)
        return

    lang = i18n.language
    if callback.from_user:
        lang = await user_repo.get_language(callback.from_user.id)
    local_i18n = I18n(lang)

    await callback.message.edit_text(
        local_i18n("analytics.common.select_period", title=channel.title),
        reply_markup=get_analytics_period_keyboard(channel_id, local_i18n),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("analytics:"))
async def on_analytics_period_select(
    callback: CallbackQuery,
    channel_repo: ChannelRepository,
    member_repo: MemberRepository,
    event_repo: EventRepository,
    user_repo: UserRepository,
    i18n: I18n,
) -> None:
    """Handle analytics period selection."""
    if not callback.data:
        return

    parts = callback.data.split(":")
    channel_id = int(parts[1])
    days = int(parts[2])

    channel = await channel_repo.get_by_id(channel_id)
    if not channel:
        await callback.answer(i18n("analytics.common.channel_not_found"), show_alert=True)
        return

    lang = i18n.language
    if callback.from_user:
        lang = await user_repo.get_language(callback.from_user.id)
    local_i18n = I18n(lang)

    analytics = AnalyticsService(member_repo, event_repo)

    growth = await analytics.get_growth_dynamics_message(channel, days, local_i18n)
    activity = await analytics.get_activity_insights_message(channel, days, local_i18n)
    audience = await analytics.get_audience_insights_message(channel, days, local_i18n)

    message_text = "\n\n".join([growth, activity, audience])

    await callback.message.edit_text(message_text)
    await callback.answer()


@router.message(Command("alerts"))
async def cmd_alerts(
    message: Message,
    channel_repo: ChannelRepository,
    alert_repo: AlertSettingsRepository,
    user_repo: UserRepository,
    i18n: I18n,
) -> None:
    """Handle /alerts command - configure alerts."""
    user = message.from_user
    if not user:
        return

    lang = await user_repo.get_language(user.id)
    local_i18n = I18n(lang)

    channels = await channel_repo.get_by_admin(user.id)
    if not channels:
        await message.answer(local_i18n("alerts.settings.no_channels"))
        return

    if len(channels) == 1:
        channel = channels[0]
        settings = await alert_repo.get_or_create(channel.id)
        summary = format_alerts_summary(channel, settings, local_i18n)
        await message.answer(
            summary,
            reply_markup=get_alerts_keyboard(channel.id, settings, local_i18n),
        )
    else:
        await message.answer(
            local_i18n("alerts.settings.select_channel"),
            reply_markup=get_channel_keyboard(channels, prefix="alertch"),
        )


@router.callback_query(F.data.startswith("alertch:"))
async def on_alerts_channel_select(
    callback: CallbackQuery,
    channel_repo: ChannelRepository,
    alert_repo: AlertSettingsRepository,
    user_repo: UserRepository,
    i18n: I18n,
) -> None:
    """Select channel for alerts."""
    if not callback.data:
        return

    channel_id = int(callback.data.split(":")[1])
    channel = await channel_repo.get_by_id(channel_id)
    if not channel:
        await callback.answer(i18n("alerts.settings.channel_not_found"), show_alert=True)
        return

    lang = i18n.language
    if callback.from_user:
        lang = await user_repo.get_language(callback.from_user.id)
    local_i18n = I18n(lang)
    settings = await alert_repo.get_or_create(channel_id)
    summary = format_alerts_summary(channel, settings, local_i18n)

    await callback.message.edit_text(
        summary,
        reply_markup=get_alerts_keyboard(channel_id, settings, local_i18n),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("alert:"))
async def on_alerts_update(
    callback: CallbackQuery,
    channel_repo: ChannelRepository,
    alert_repo: AlertSettingsRepository,
    user_repo: UserRepository,
    i18n: I18n,
) -> None:
    """Handle alert setting changes."""
    if not callback.data:
        return
    parts = callback.data.split(":")
    if len(parts) < 4:
        return
    action = parts[1]
    channel_id = int(parts[2])
    value = parts[3]

    channel = await channel_repo.get_by_id(channel_id)
    if not channel:
        await callback.answer(i18n("alerts.settings.channel_not_found"), show_alert=True)
        return

    lang = i18n.language
    if callback.from_user:
        lang = await user_repo.get_language(callback.from_user.id)
    local_i18n = I18n(lang)

    # Update settings
    if action == "mlt":
        await alert_repo.update(channel_id, mass_leave_threshold=int(value))
    elif action == "mlw":
        await alert_repo.update(channel_id, mass_leave_window_minutes=int(value))
    elif action == "af":
        await alert_repo.update(channel_id, anomaly_factor=float(value))
    elif action == "ms":
        await alert_repo.update(channel_id, milestone_step=int(value))
    elif action == "ct":
        await alert_repo.update(channel_id, churn_percent_threshold=float(value))
    elif action == "dd":
        await alert_repo.update(channel_id, digest_daily=(value == "on"))
    elif action == "wd":
        await alert_repo.update(channel_id, digest_weekly=(value == "on"))
    elif action == "md":
        await alert_repo.update(channel_id, digest_monthly=(value == "on"))
    elif action == "qh":
        start_str, end_str = value.split("-")
        await alert_repo.update(
            channel_id,
            quiet_hours_start=int(start_str),
            quiet_hours_end=int(end_str),
        )
    elif action == "vipclear":
        await alert_repo.set_vips(channel_id, [])

    # Refresh summary
    settings = await alert_repo.get_or_create(channel_id)
    summary = format_alerts_summary(channel, settings, local_i18n)
    await callback.message.edit_text(
        summary,
        reply_markup=get_alerts_keyboard(channel_id, settings, local_i18n),
    )
    await callback.answer(local_i18n("alerts.settings.updated"))


@router.message(Command("vip_add"))
async def cmd_vip_add(
    message: Message,
    alert_repo: AlertSettingsRepository,
    channel_repo: ChannelRepository,
    user_repo: UserRepository,
    i18n: I18n,
) -> None:
    """Add VIP user IDs for alerts."""
    user = message.from_user
    if not user:
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(i18n("alerts.settings.vip_usage"))
        return

    ids = []
    for token in parts[1:]:
        if token.isdigit():
            ids.append(int(token))

    channels = await channel_repo.get_by_admin(user.id)
    if not channels:
        await message.answer(i18n("alerts.settings.no_channels"))
        return

    # apply to all channels of admin
    for channel in channels:
        await alert_repo.set_vips(channel.id, ids)

    lang = await user_repo.get_language(user.id)
    local_i18n = I18n(lang)
    await message.answer(local_i18n("alerts.settings.vips_set", vips=", ".join(map(str, ids))))


@router.message(Command("vip_clear"))
async def cmd_vip_clear(
    message: Message,
    alert_repo: AlertSettingsRepository,
    channel_repo: ChannelRepository,
    user_repo: UserRepository,
    i18n: I18n,
) -> None:
    """Clear VIP user IDs."""
    user = message.from_user
    if not user:
        return

    channels = await channel_repo.get_by_admin(user.id)
    if not channels:
        await message.answer(i18n("alerts.settings.no_channels"))
        return

    for channel in channels:
        await alert_repo.set_vips(channel.id, [])

    lang = await user_repo.get_language(user.id)
    local_i18n = I18n(lang)
    await message.answer(local_i18n("alerts.settings.vips_cleared"))


@router.message(Command("sheets"))
async def cmd_sheets(
    message: Message,
    google_repo: GoogleSettingsRepository,
    i18n: I18n,
) -> None:
    """Show Sheets settings info."""
    user = message.from_user
    if not user:
        return
    settings = await google_repo.get(user.id)
    has_creds = bool(settings and settings.creds_json)
    has_sheet = bool(settings and settings.spreadsheet_id)
    status_lines = [
        i18n("export.sheets_status", creds=i18n('export.status_set') if has_creds else i18n('export.status_not_set'), sheet=settings.spreadsheet_id if has_sheet else i18n('export.status_not_set')),
        i18n("export.sheets_instruction_upload"),
        i18n("export.sheets_instruction_id"),
        i18n("export.sheets_instruction_clear"),
    ]
    await message.answer("\n".join(status_lines))


@router.message(Command("sheet_id"))
async def cmd_sheet_id(
    message: Message,
    google_repo: GoogleSettingsRepository,
    i18n: I18n,
) -> None:
    """Set spreadsheet ID."""
    user = message.from_user
    if not user:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Use: /sheet_id <spreadsheet_id>")
        return
    sheet_id = parts[1].strip()
    await google_repo.set_spreadsheet(user.id, sheet_id)
    await message.answer(i18n("export.sheet_set"))


@router.message(Command("sheets_clear"))
async def cmd_sheets_clear(
    message: Message,
    google_repo: GoogleSettingsRepository,
    i18n: I18n,
) -> None:
    """Clear Sheets settings."""
    user = message.from_user
    if not user:
        return
    await google_repo.clear(user.id)
    await message.answer(i18n("export.cleared"))


@router.message(F.document)
async def on_document_upload(
    message: Message,
    google_repo: GoogleSettingsRepository,
    i18n: I18n,
    bot: Bot,
) -> None:
    """Capture service account JSON upload."""
    user = message.from_user
    if not user or not message.document:
        return
    filename = message.document.file_name or ""
    if not filename.lower().endswith(".json"):
        return
    file = await bot.get_file(message.document.file_id)
    file_bytes = await bot.download_file(file.file_path)
    content = file_bytes.read().decode("utf-8")
    await google_repo.upsert_creds(user.id, content)
    await message.answer(i18n("export.creds_set"))
@router.message(Command("recent"))
async def cmd_recent(
    message: Message,
    channel_repo: ChannelRepository,
    member_repo: MemberRepository,
    event_repo: EventRepository,
    google_repo: GoogleSettingsRepository,
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
    """Handle /export command - choose format."""
    user = message.from_user
    if not user:
        return

    channels = await channel_repo.get_by_admin(user.id)

    if not channels:
        await message.answer(i18n("export.no_channels"))
        return

    if len(channels) == 1:
        await message.answer(
            i18n("export.select_format", title=channels[0].title),
            reply_markup=get_export_format_keyboard(channels[0].id, i18n),
        )
    else:
        await message.answer(
            i18n("export.select_channel"),
            reply_markup=get_channel_keyboard(channels, prefix="exportch"),
        )


@router.callback_query(F.data.startswith("exportch:"))
async def on_export_channel_select(
    callback: CallbackQuery,
    channel_repo: ChannelRepository,
    google_repo: GoogleSettingsRepository,
    i18n: I18n,
) -> None:
    """Select channel for export."""
    if not callback.data:
        return

    channel_id = int(callback.data.split(":")[1])
    channel = await channel_repo.get_by_id(channel_id)
    if not channel:
        await callback.answer(i18n("export.channel_not_found"), show_alert=True)
        return

    await callback.message.edit_text(
        i18n("export.select_format", title=channel.title),
        reply_markup=get_export_format_keyboard(channel_id, i18n),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("export:"))
async def on_export_format_select(
    callback: CallbackQuery,
    channel_repo: ChannelRepository,
    member_repo: MemberRepository,
    event_repo: EventRepository,
    google_repo: GoogleSettingsRepository,
    i18n: I18n,
) -> None:
    """Handle export format selection."""
    if not callback.data:
        return
    parts = callback.data.split(":")
    channel_id = int(parts[1])
    fmt = parts[2]

    channel = await channel_repo.get_by_id(channel_id)
    if not channel:
        await callback.answer(i18n("export.channel_not_found"), show_alert=True)
        return

    analytics = AnalyticsService(member_repo, event_repo)
    reports = ReportsService(event_repo, member_repo)
    user_settings = None
    if callback.from_user:
        user_settings = await google_repo.get(callback.from_user.id)

    if fmt == "csv":
        csv_file = await analytics.export_events_csv(channel)
        await callback.message.answer_document(
            csv_file,
            caption=i18n("export.caption", title=channel.title),
        )
    elif fmt == "pdf":
        pdf_file = await reports.export_pdf(channel)
        await callback.message.answer_document(
            pdf_file,
            caption=i18n("export.caption_pdf", title=channel.title),
        )
    elif fmt == "json":
        json_file = await reports.export_json(channel)
        await callback.message.answer_document(
            json_file,
            caption=i18n("export.caption_json", title=channel.title),
        )
    elif fmt == "sheets":
        creds_json = user_settings.creds_json if user_settings else None
        sheet_id = user_settings.spreadsheet_id if user_settings else None
        success = await reports.export_to_sheets(channel, creds_json=creds_json, spreadsheet_id=sheet_id)
        if success:
            await callback.message.answer(i18n("export.sheets_success", title=channel.title))
        else:
            await callback.message.answer(i18n("export.sheets_fail"))

    await callback.answer()


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
