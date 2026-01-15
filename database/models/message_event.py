"""Message event model for tracking comments, reactions, etc."""

from sqlalchemy import BigInteger, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, TimestampMixin


class MessageEvent(Base, TimestampMixin):
    """Event tracking message activities (comments, reactions, forwards)."""

    __tablename__ = "message_events"

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
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content_preview: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    channel: Mapped["Channel"] = relationship("Channel", back_populates="message_events")  # noqa: F821

    __table_args__ = (
        Index("ix_message_events_channel", "channel_id"),
        Index("ix_message_events_user", "user_id"),
        Index("ix_message_events_type", "event_type"),
        Index("ix_message_events_created", "created_at"),
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

    def __repr__(self) -> str:
        return f"<MessageEvent(type='{self.event_type}', message_id={self.message_id})>"
