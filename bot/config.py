"""Bot configuration using pydantic-settings."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Bot settings
    bot_token: SecretStr

    # Database settings
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/channel_analytics_bot"

    # Admin settings
    admin_ids: str = ""

    # Logging
    log_level: str = "INFO"

    @property
    def admin_id_list(self) -> list[int]:
        """Parse admin IDs from comma-separated string."""
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]


settings = Settings()
