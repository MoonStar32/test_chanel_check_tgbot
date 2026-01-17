"""Alert settings for channels."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, TimestampMixin


class AlertSettings(Base, TimestampMixin):
    """Per-channel alert configuration and state."""

    __tablename__ = "alert_settings"

    channel_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("channels.id", ondelete="CASCADE"),
        primary_key=True,
    )
    mass_leave_threshold: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    mass_leave_window_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    anomaly_factor: Mapped[float] = mapped_column(Float, default=3.0, nullable=False)
    milestone_step: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    last_milestone: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    digest_daily: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    digest_weekly: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    digest_monthly: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    quiet_hours_start: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-23
    quiet_hours_end: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-23
    churn_percent_threshold: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    vip_user_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_churn_alert_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_daily_digest: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_weekly_digest: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_monthly_digest: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    channel: Mapped["Channel"] = relationship("Channel", back_populates="alert_settings")  # noqa: F821

    def vip_id_list(self) -> list[int]:
        """Parse VIP user IDs from text."""
        if not self.vip_user_ids:
            return []
        return [int(x) for x in self.vip_user_ids.split(",") if x.strip().isdigit()]
