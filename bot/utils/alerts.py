"""Formatting helpers for alert settings."""

from bot.i18n import I18n
from database.models import AlertSettings, Channel


def format_alerts_summary(
    channel: Channel,
    settings: AlertSettings,
    i18n: I18n,
) -> str:
    """Build a summary of alert settings."""
    vip_list = settings.vip_id_list()
    quiet = f"{settings.quiet_hours_start:02d}:00-{settings.quiet_hours_end:02d}:00" if settings.quiet_hours_start or settings.quiet_hours_end else i18n("alerts.settings.quiet_off")
    summary = [
        i18n("alerts.settings.title", title=channel.title),
        i18n("alerts.settings.mass_leave", count=settings.mass_leave_threshold, minutes=settings.mass_leave_window_minutes),
        i18n("alerts.settings.anomaly", factor=settings.anomaly_factor),
        i18n("alerts.settings.milestone", step=settings.milestone_step, last=settings.last_milestone),
        i18n("alerts.settings.churn", threshold=f"{settings.churn_percent_threshold:.1f}%"),
        i18n("alerts.settings.daily", state=_on_off(settings.digest_daily, i18n)),
        i18n("alerts.settings.weekly", state=_on_off(settings.digest_weekly, i18n)),
        i18n("alerts.settings.monthly", state=_on_off(settings.digest_monthly, i18n)),
        i18n("alerts.settings.quiet", quiet=quiet),
        i18n("alerts.settings.vips", vips=", ".join(map(str, vip_list)) if vip_list else i18n("alerts.settings.vips_none")),
    ]
    return "\n".join(summary)


def _on_off(value: bool, i18n: I18n) -> str:
    return i18n("alerts.settings.on") if value else i18n("alerts.settings.off")
