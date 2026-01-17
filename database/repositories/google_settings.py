"""Repository for per-user Google Sheets settings."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import GoogleSettings


class GoogleSettingsRepository:
    """CRUD operations for GoogleSettings."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: int) -> GoogleSettings | None:
        result = await self.session.execute(
            select(GoogleSettings).where(GoogleSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert_creds(self, user_id: int, creds_json: str) -> GoogleSettings:
        settings = await self.get(user_id)
        if settings:
            await self.session.execute(
                update(GoogleSettings)
                .where(GoogleSettings.user_id == user_id)
                .values(creds_json=creds_json)
            )
        else:
            self.session.add(GoogleSettings(user_id=user_id, creds_json=creds_json))
        await self.session.commit()
        return await self.get(user_id)  # type: ignore[return-value]

    async def set_spreadsheet(self, user_id: int, spreadsheet_id: str) -> GoogleSettings:
        settings = await self.get(user_id)
        if settings:
            await self.session.execute(
                update(GoogleSettings)
                .where(GoogleSettings.user_id == user_id)
                .values(spreadsheet_id=spreadsheet_id)
            )
        else:
            self.session.add(GoogleSettings(user_id=user_id, spreadsheet_id=spreadsheet_id))
        await self.session.commit()
        return await self.get(user_id)  # type: ignore[return-value]

    async def clear(self, user_id: int) -> None:
        await self.session.execute(
            update(GoogleSettings)
            .where(GoogleSettings.user_id == user_id)
            .values(creds_json=None, spreadsheet_id=None)
        )
        await self.session.commit()
