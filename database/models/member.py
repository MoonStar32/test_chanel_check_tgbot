"""Member model for tracking channel subscribers."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, TimestampMixin


class Member(Base, TimestampMixin):
    """Channel member/subscriber."""

    __tablename__ = "members"

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
    status: Mapped[str] = mapped_column(String(50), default="member", nullable=False)
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    channel: Mapped["Channel"] = relationship("Channel", back_populates="members")  # noqa: F821

    __table_args__ = (
        Index("ix_members_channel_user", "channel_id", "user_id", unique=True),
        Index("ix_members_status", "status"),
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
        return f"<Member(user_id={self.user_id}, status='{self.status}')>"
