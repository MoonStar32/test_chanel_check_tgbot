"""Bot and dispatcher initialization."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from bot.config import settings

# aiogram expects session.timeout to be numeric (seconds) for polling math.
# Use float timeout to avoid TypeError when adding polling_timeout.
session = AiohttpSession(timeout=60)

bot = Bot(
    token=settings.bot_token.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session,
)

dp = Dispatcher()
