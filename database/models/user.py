"""User model for storing user preferences."""

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Telegram user with preferences."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, language='{self.language}')>"
