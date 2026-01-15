"""Core i18n functionality."""

from typing import Any

from bot.i18n.locales import LOCALES

SUPPORTED_LANGUAGES = ["en", "ru"]
DEFAULT_LANGUAGE = "en"


class I18n:
    """Internationalization helper class."""

    def __init__(self, language: str = DEFAULT_LANGUAGE) -> None:
        self.language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

    def get(self, key: str, **kwargs: Any) -> str:
        """Get translated text by key with optional formatting."""
        locale = LOCALES.get(self.language, LOCALES[DEFAULT_LANGUAGE])

        keys = key.split(".")
        value = locale
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                value = None
                break

        if value is None:
            fallback = LOCALES[DEFAULT_LANGUAGE]
            for k in keys:
                if isinstance(fallback, dict):
                    fallback = fallback.get(k)
                else:
                    fallback = None
                    break
            value = fallback

        if value is None:
            return key

        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                return value

        return value

    def __call__(self, key: str, **kwargs: Any) -> str:
        """Shortcut for get method."""
        return self.get(key, **kwargs)


def get_text(language: str, key: str, **kwargs: Any) -> str:
    """Get translated text by language and key."""
    return I18n(language).get(key, **kwargs)
