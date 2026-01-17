"""Alert and digest service."""

import asyncio
from datetime import datetime, timedelta, timezone

from loguru import logger

from aiogram import Bot

from bot.i18n import I18n
from bot.services.analytics import AnalyticsService
from bot.services.notifications import NotificationService
from database.models import AlertSettings, Channel
from database.repositories import (
    AlertSettingsRepository,
    ChannelRepository,
    EventRepository,
    MemberRepository,
    UserRepository,
)


class AlertService:
    """Encapsulates alert logic for events and scheduled digests."""

    def __init__(
        self,
        bot: Bot,
        event_repo: EventRepository,
        member_repo: MemberRepository,
        alert_repo: AlertSettingsRepository,
        user_repo: UserRepository,
    ) -> None:
        self.bot = bot
        self.event_repo = event_repo
        self.member_repo = member_repo
        self.alert_repo = alert_repo
        self.user_repo = user_repo

    async def handle_member_event_alerts(
        self,
        channel: Channel,
        settings: AlertSettings,
        event_type: str,
        user_id: int,
        event_time: datetime,
    ) -> None:
        """Run alert checks after a member event."""
        if not channel.notify_chat_id:
            return

        if self._is_quiet(settings, event_time):
            logger.debug("Quiet hours active; skipping alerts")
            return

        admin_lang = await self.user_repo.get_language(channel.admin_user_id)
        i18n = I18n(admin_lang)
        notifier = NotificationService(self.bot, i18n)

        await self._check_mass_leaves(channel, settings, notifier)
        await self._check_anomaly(channel, settings, notifier)
        await self._check_milestone(channel, settings, notifier)
        await self._check_churn_threshold(channel, settings, notifier, event_time)
        await self._check_vip_leave(channel, settings, notifier, event_type, user_id)

    async def _check_mass_leaves(
        self,
        channel: Channel,
        settings: AlertSettings,
        notifier: NotificationService,
    ) -> None:
        window_start = datetime.now(timezone.utc) - timedelta(
            minutes=settings.mass_leave_window_minutes
        )
        recent_leaves = await self.event_repo.count_member_events(
            channel.id,
            event_type="leave",
            since=window_start,
        )
        if recent_leaves >= settings.mass_leave_threshold:
            msg = notifier.i18n(
                "alerts.mass_leave",
                title=channel.title,
                count=recent_leaves,
                minutes=settings.mass_leave_window_minutes,
            )
            await notifier.send_text(channel.notify_chat_id, msg)

    async def _check_anomaly(
        self,
        channel: Channel,
        settings: AlertSettings,
        notifier: NotificationService,
    ) -> None:
        now = datetime.now(timezone.utc)
        last_hour = await self.event_repo.count_member_events(
            channel.id,
            since=now - timedelta(hours=1),
        )
        last_day = await self.event_repo.count_member_events(
            channel.id,
            since=now - timedelta(hours=24),
        )
        baseline_hours = max(1, 23)
        baseline = max(1, (last_day - last_hour) / baseline_hours)
        if last_hour >= settings.anomaly_factor * baseline and last_hour >= 5:
            msg = notifier.i18n(
                "alerts.anomaly_spike",
                title=channel.title,
                count=last_hour,
            )
            await notifier.send_text(channel.notify_chat_id, msg)
        elif baseline >= settings.anomaly_factor * max(1, last_hour):
            msg = notifier.i18n(
                "alerts.anomaly_drop",
                title=channel.title,
            )
            await notifier.send_text(channel.notify_chat_id, msg)

    async def _check_milestone(
        self,
        channel: Channel,
        settings: AlertSettings,
        notifier: NotificationService,
    ) -> None:
        member_counts = await self.member_repo.count_by_status(channel.id)
        active = member_counts.get("member", 0)
        step = max(1, settings.milestone_step)
        milestone_reached = (active // step) * step
        if milestone_reached > settings.last_milestone:
            await self.alert_repo.set_last_milestone(channel.id, milestone_reached)
            msg = notifier.i18n(
                "alerts.milestone",
                title=channel.title,
                milestone=milestone_reached,
            )
            await notifier.send_text(channel.notify_chat_id, msg)

    async def _check_churn_threshold(
        self,
        channel: Channel,
        settings: AlertSettings,
        notifier: NotificationService,
        event_time: datetime,
    ) -> None:
        if settings.churn_percent_threshold <= 0:
            return
        if settings.last_churn_alert_at:
            # avoid spamming: one alert per 6h
            if (event_time - settings.last_churn_alert_at) < timedelta(hours=6):
                return
        window_start = event_time - timedelta(days=1)
        leaves = await self.event_repo.count_member_events(
            channel.id,
            event_type="leave",
            since=window_start,
        )
        member_counts = await self.member_repo.count_by_status(channel.id)
        active = member_counts.get("member", 0)
        total = active + member_counts.get("left", 0)
        if total == 0:
            return
        churn = (leaves / total) * 100
        if churn >= settings.churn_percent_threshold:
            await self.alert_repo.set_last_churn_alert(channel.id, event_time)
            msg = notifier.i18n(
                "alerts.churn_threshold",
                title=channel.title,
                churn=f"{churn:.1f}%",
                threshold=f"{settings.churn_percent_threshold:.1f}%",
            )
            await notifier.send_text(channel.notify_chat_id, msg)

    async def _check_vip_leave(
        self,
        channel: Channel,
        settings: AlertSettings,
        notifier: NotificationService,
        event_type: str,
        user_id: int,
    ) -> None:
        if event_type not in ("leave", "kick", "ban"):
            return
        vip_ids = settings.vip_id_list()
        if user_id in vip_ids:
            msg = notifier.i18n(
                "alerts.vip_left",
                title=channel.title,
                user_id=user_id,
            )
            await notifier.send_text(channel.notify_chat_id, msg)

    def _is_quiet(self, settings: AlertSettings, event_time: datetime) -> bool:
        """Check quiet hours window."""
        start = settings.quiet_hours_start
        end = settings.quiet_hours_end
        if start == end == 0:
            return False
        hour = event_time.hour
        if start <= end:
            return start <= hour < end
        return hour >= start or hour < end


async def run_digest_worker(
    bot: Bot,
    interval_seconds: int = 900,
) -> None:
    """Periodic task to send daily/weekly digests."""
    from database import async_session_maker

    while True:
        try:
            async with async_session_maker() as session:
                channel_repo = ChannelRepository(session)
                event_repo = EventRepository(session)
                member_repo = MemberRepository(session)
                alert_repo = AlertSettingsRepository(session)
                user_repo = UserRepository(session)

                channels = await channel_repo.get_all_active()
                now = datetime.now(timezone.utc)

                for channel in channels:
                    if not channel.notify_chat_id:
                        continue

                    settings = await alert_repo.get_or_create(channel.id)
                    alert_service = AlertService(
                        bot, event_repo, member_repo, alert_repo, user_repo
                    )
                    if alert_service._is_quiet(settings, now):
                        continue

                    admin_lang = await user_repo.get_language(channel.admin_user_id)
                    i18n = I18n(admin_lang)
                    notifier = NotificationService(bot, i18n)
                    analytics = AnalyticsService(member_repo, event_repo)

                    # Daily digest at 09:00 UTC
                    if settings.digest_daily and now.hour == 9:
                        if not settings.last_daily_digest or settings.last_daily_digest.date() < now.date():
                            digest = await analytics.get_growth_dynamics_message(channel, days=1, i18n=i18n)
                            digest += "\n\n" + await analytics.get_activity_insights_message(channel, days=7, i18n=i18n)
                            await notifier.send_text(channel.notify_chat_id, i18n("alerts.digest_daily_prefix") + "\n\n" + digest)
                            await alert_repo.set_last_daily_digest(channel.id, now)

                    # Weekly digest Monday 09:05 UTC
                    if settings.digest_weekly and now.weekday() == 0 and now.hour == 9 and now.minute >= 5:
                        if not settings.last_weekly_digest or settings.last_weekly_digest.date() < now.date():
                            digest = await analytics.get_growth_dynamics_message(channel, days=7, i18n=i18n)
                            await notifier.send_text(channel.notify_chat_id, i18n("alerts.digest_weekly_prefix") + "\n\n" + digest)
                            await alert_repo.set_last_weekly_digest(channel.id, now)

                    # Monthly digest on 1st day 09:10 UTC
                    if settings.digest_monthly and now.day == 1 and now.hour == 9 and now.minute >= 10:
                        if not settings.last_monthly_digest or settings.last_monthly_digest.date() < now.date():
                            digest = await analytics.get_growth_dynamics_message(channel, days=30, i18n=i18n)
                            await notifier.send_text(channel.notify_chat_id, i18n("alerts.digest_monthly_prefix") + "\n\n" + digest)
                            await alert_repo.set_last_monthly_digest(channel.id, now)
        except Exception as e:
            logger.error(f"Digest worker error: {e}")

        await asyncio.sleep(interval_seconds)
