"""Bot handlers."""

from aiogram import Router

from bot.handlers.admin import router as admin_router
from bot.handlers.channel_events import router as channel_events_router
from bot.handlers.messages import router as messages_router


def setup_routers() -> Router:
    """Setup and combine all routers."""
    main_router = Router()

    main_router.include_router(channel_events_router)
    main_router.include_router(admin_router)
    main_router.include_router(messages_router)

    return main_router
