"""Bot entry point."""

import asyncio
import sys

from loguru import logger

from bot.config import settings
from bot.handlers import setup_routers
from bot.loader import bot, dp
from bot.middlewares import DatabaseMiddleware
from database import init_db


def setup_logging() -> None:
    """Configure loguru logging."""
    logger.remove()
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=settings.log_level,
        colorize=True,
    )
    logger.add(
        "logs/bot_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    )


async def on_startup() -> None:
    """Actions on bot startup."""
    logger.info("Starting bot...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Setup routers
    main_router = setup_routers()
    dp.include_router(main_router)

    # Setup middlewares
    dp.update.middleware(DatabaseMiddleware())

    logger.info("Bot started successfully!")


async def on_shutdown() -> None:
    """Actions on bot shutdown."""
    logger.info("Shutting down bot...")
    await bot.session.close()
    logger.info("Bot stopped")


async def main() -> None:
    """Main function to run the bot."""
    setup_logging()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        logger.info("Bot is starting polling...")
        await dp.start_polling(
            bot,
            allowed_updates=[
                "message",
                "callback_query",
                "chat_member",
                "my_chat_member",
                "channel_post",
            ],
        )
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
