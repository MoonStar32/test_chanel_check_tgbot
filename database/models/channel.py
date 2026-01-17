"""Channel model for tracking monitored channels."""

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, TimestampMixin


class Channel(Base, TimestampMixin):
    """Telegram channel being monitored."""

    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    admin_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    notify_chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    members: Mapped[list["Member"]] = relationship(  # noqa: F821
        "Member",
        back_populates="channel",
        lazy="selectin",
    )
    member_events: Mapped[list["MemberEvent"]] = relationship(  # noqa: F821
        "MemberEvent",
        back_populates="channel",
        lazy="selectin",
    )
    message_events: Mapped[list["MessageEvent"]] = relationship(  # noqa: F821
        "MessageEvent",
        back_populates="channel",
        lazy="selectin",
    )
    alert_settings: Mapped["AlertSettings"] = relationship(  # noqa: F821
        "AlertSettings",
        back_populates="channel",
        uselist=False,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Channel(id={self.id}, title='{self.title}')>"
