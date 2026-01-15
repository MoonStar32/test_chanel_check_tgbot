"""Database session middleware."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.i18n import I18n
from database import async_session_maker
from database.repositories import (
    ChannelRepository,
    EventRepository,
    MemberRepository,
    UserRepository,
)


class DatabaseMiddleware(BaseMiddleware):
    """Middleware that provides database session, repositories, and i18n to handlers."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with async_session_maker() as session:
            data["session"] = session
            data["channel_repo"] = ChannelRepository(session)
            data["member_repo"] = MemberRepository(session)
            data["event_repo"] = EventRepository(session)
            data["user_repo"] = UserRepository(session)

            # Get user language for i18n
            user_id = None
            if hasattr(event, "from_user") and event.from_user:
                user_id = event.from_user.id
            elif hasattr(event, "message") and event.message and event.message.from_user:
                user_id = event.message.from_user.id

            language = "en"
            if user_id:
                language = await data["user_repo"].get_language(user_id)

            data["i18n"] = I18n(language)
            data["_"] = data["i18n"]  # Shortcut

            return await handler(event, data)
