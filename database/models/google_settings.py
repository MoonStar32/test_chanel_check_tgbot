"""Per-user Google Sheets settings."""

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base, TimestampMixin


class GoogleSettings(Base, TimestampMixin):
    """Stores per-user Google Sheets credentials and spreadsheet id."""

    __tablename__ = "google_settings"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    creds_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    spreadsheet_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
