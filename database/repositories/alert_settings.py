"""Alert settings repository."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import AlertSettings


class AlertSettingsRepository:
    """Repository for alert settings per channel."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_channel(self, channel_id: int) -> AlertSettings | None:
        result = await self.session.execute(
            select(AlertSettings).where(AlertSettings.channel_id == channel_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, channel_id: int) -> AlertSettings:
        settings = await self.get_by_channel(channel_id)
        if settings:
            return settings
        settings = AlertSettings(channel_id=channel_id)
        self.session.add(settings)
        await self.session.commit()
        await self.session.refresh(settings)
        return settings

    async def update(self, channel_id: int, **kwargs) -> AlertSettings:
        await self.session.execute(
            update(AlertSettings)
            .where(AlertSettings.channel_id == channel_id)
            .values(**kwargs)
        )
        await self.session.commit()
        return await self.get_or_create(channel_id)

    async def set_last_milestone(self, channel_id: int, milestone: int) -> AlertSettings:
        return await self.update(channel_id, last_milestone=milestone)

    async def set_last_churn_alert(self, channel_id: int, dt) -> AlertSettings:
        return await self.update(channel_id, last_churn_alert_at=dt)

    async def set_last_daily_digest(self, channel_id: int, dt) -> AlertSettings:
        return await self.update(channel_id, last_daily_digest=dt)

    async def set_last_weekly_digest(self, channel_id: int, dt) -> AlertSettings:
        return await self.update(channel_id, last_weekly_digest=dt)

    async def set_vips(self, channel_id: int, ids: list[int]) -> AlertSettings:
        payload = ",".join(str(x) for x in ids)
        return await self.update(channel_id, vip_user_ids=payload)

    async def set_last_monthly_digest(self, channel_id: int, dt) -> AlertSettings:
        return await self.update(channel_id, last_monthly_digest=dt)
