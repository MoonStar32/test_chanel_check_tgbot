"""Admin filter for restricting commands."""

from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.config import settings


class AdminFilter(BaseFilter):
    """Filter that allows only admin users."""

    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        return message.from_user.id in settings.admin_id_list
