"""Locale files."""

from bot.i18n.locales.en import LOCALE as EN_LOCALE
from bot.i18n.locales.ru import LOCALE as RU_LOCALE

LOCALES = {
    "en": EN_LOCALE,
    "ru": RU_LOCALE,
}

__all__ = ["LOCALES"]
