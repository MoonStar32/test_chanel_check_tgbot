"""Member event model for tracking join/leave events."""

from sqlalchemy import BigInteger, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, TimestampMixin


class MemberEvent(Base, TimestampMixin):
    """Event tracking member status changes (join, leave, kick, ban)."""

    __tablename__ = "member_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    inviter_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Relationships
    channel: Mapped["Channel"] = relationship("Channel", back_populates="member_events")  # noqa: F821

    __table_args__ = (
        Index("ix_member_events_channel", "channel_id"),
        Index("ix_member_events_user", "user_id"),
        Index("ix_member_events_type", "event_type"),
        Index("ix_member_events_created", "created_at"),
    )

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else "Unknown"

    @property
    def mention(self) -> str:
        """Get user mention or name."""
        if self.username:
            return f"@{self.username}"
        return self.full_name

    def __repr__(self) -> str:
        return f"<MemberEvent(type='{self.event_type}', user_id={self.user_id})>"
