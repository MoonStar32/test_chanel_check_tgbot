"""Russian locale."""

LOCALE = {
    "language": {
        "name": "Русский",
        "flag": "\U0001F1F7\U0001F1FA",
        "select": "Выберите язык:",
        "changed": "Язык изменён на русский",
    },
    "start": {
        "title": "<b>Бот Аналитики Каналов</b>",
        "description": (
            "Я отслеживаю активность подписчиков канала:\n"
            "  - Новые подписки\n"
            "  - Отписки\n"
            "  - Кики и баны\n"
            "  - Комментарии (в связанных группах)"
        ),
        "how_to_use": (
            "<b>Как использовать:</b>\n"
            "1. Добавьте меня в канал как администратора\n"
            "2. Дайте мне право видеть участников канала\n"
            "3. Я буду отправлять уведомления о всех событиях"
        ),
        "commands": (
            "<b>Команды:</b>\n"
            "/stats - Статистика канала\n"
            "/recent - Последние события\n"
            "/left - Кто недавно отписался\n"
            "/export - Экспорт в CSV\n"
            "/analytics - Расширенная аналитика\n"
            "/setchat - Установить чат для уведомлений\n"
            "/language - Сменить язык"
        ),
        "your_channels": "Ваши каналы ({count}):",
        "no_channels": "Каналов пока нет. Добавьте меня в канал, чтобы начать!",
        "channel_active": "активен",
        "channel_inactive": "неактивен",
    },
    "stats": {
        "select_channel": "Выберите канал:",
        "select_period": "Выберите период для <b>{title}</b>:",
        "no_channels": (
            "У вас пока нет каналов.\n"
            "Сначала добавьте меня в канал как администратора!"
        ),
        "channel_not_found": "Канал не найден",
        "title": "<b>{title}</b>",
        "period": "Статистика за {period}",
        "period_days": "последние {days} дней",
        "period_all": "всё время",
        "current_state": "<b>Текущее состояние:</b>",
        "active_members": "Активных участников: {count}",
        "left_members": "Отписались: {count}",
        "events": "<b>События:</b>",
        "joins": "Подписок: {count}",
        "leaves": "Отписок: {count}",
        "kicks": "Киков: {count}",
        "bans": "Банов: {count}",
        "net_change": "Изменение: {change}",
    },
    "recent": {
        "title": "<b>Последние события в {title}:</b>",
        "no_events": "Нет недавних событий для <b>{title}</b>",
        "no_channels": "У вас пока нет каналов.",
    },
    "left": {
        "title": "<b>Отписались от {title} (последние {days} дней):</b>",
        "no_one_left": "Никто не отписался от <b>{title}</b> за последние {days} дней",
        "total": "Всего: {count}",
        "no_channels": "У вас пока нет каналов.",
    },
    "export": {
        "caption": "Экспорт событий для {title}",
        "no_channels": "У вас пока нет каналов.",
        "select_channel": "Выберите канал для экспорта:",
        "select_format": "Выберите формат экспорта для <b>{title}</b>:",
        "channel_not_found": "Канал не найден",
        "caption_pdf": "PDF отчёт для {title}",
        "caption_json": "JSON экспорт для {title}",
        "sheets_success": "Выгрузка в Google Sheets выполнена для {title}",
        "sheets_fail": "Google Sheets не настроен.",
        "creds_set": "Google-учётные данные сохранены.",
        "sheet_set": "ID таблицы сохранён.",
        "cleared": "Настройки экспорта в Google очищены.",
        "need_creds": "Укажите ключ и таблицу через /sheets.",
    },
    "setchat": {
        "success": "Уведомления для {count} канала(ов) будут отправляться в этот чат.",
        "no_channels": "У вас пока нет каналов.",
    },
    "help": {
        "title": "<b>Бот Аналитики Каналов - Помощь</b>",
        "setup": (
            "<b>Настройка:</b>\n"
            "1. Добавьте бота в канал как админа\n"
            "2. Дайте право 'Видеть участников'\n"
            "3. Бот автоматически зарегистрирует канал"
        ),
        "commands": (
            "<b>Команды:</b>\n"
            "/start - Приветствие и список каналов\n"
            "/stats - Статистика канала\n"
            "/recent - Последние события\n"
            "/left - Кто отписался от канала\n"
            "/export - Экспорт событий в CSV\n"
            "/analytics - Расширенная аналитика\n"
            "/alerts - Настройки алёртов\n"
            "/setchat - Куда отправлять уведомления\n"
            "/language - Сменить язык\n"
            "/help - Это сообщение"
        ),
        "tracked_events": (
            "<b>Отслеживаемые события:</b>\n"
            "  - Новые подписчики\n"
            "  - Отписки (главная фича!)\n"
            "  - Кики и баны\n"
            "  - Комментарии в связанных группах"
        ),
    },
    "welcome": {
        "added": "Бот добавлен в <b>{title}</b>!",
        "tracking": (
            "Я буду отслеживать активность участников:\n"
            "  - Новые подписчики\n"
            "  - Отписки\n"
            "  - Кики и баны"
        ),
        "notifications": "Уведомления будут отправляться сюда.",
        "commands": (
            "Используйте /stats для просмотра статистики.\n"
            "Используйте /recent для последних событий."
        ),
    },
    "events": {
        "join": "подписался на",
        "leave": "отписался от",
        "kick": "был удалён из",
        "ban": "был забанен в",
        "unban": "был разбанен в",
        "status_change": "статус изменился в",
        "user_id": "ID пользователя:",
    },
    "buttons": {
        "24_hours": "24 часа",
        "7_days": "7 дней",
        "30_days": "30 дней",
        "all_time": "За всё время",
        "back": "Назад",
    },
    "common": {
        "unknown": "Неизвестно",
    },
    "analytics": {
        "common": {
            "select_channel": "Выберите канал для аналитики:",
            "select_period": "Выберите период для <b>{title}</b>:",
            "no_channels": "У вас пока нет каналов.",
            "channel_not_found": "Канал не найден",
        },
        "growth": {
            "title": "<b>Рост для {title}</b>",
            "summary": "Подписок: {joins}, Отписок: {leaves}, Чистый прирост: {net}",
            "churn_retention": "Отток: {churn}, Удержание: {retention}",
            "forecast": "Прогноз на 7 дн.: {forecast} (среднее/день {avg})",
            "trend_header": "Динамика по дням (последние 10):",
        },
        "activity": {
            "title": "<b>Активность для {title}</b>",
            "best_hours": "<b>Топ часы (UTC):</b>",
            "hour_line": "  {hour:02d}:00 — подписок {joins} (чистый {net})",
            "best_days": "<b>Топ дни недели (0=Вск):</b>",
            "day_line": "  {dow} — подписок {joins}",
            "no_data": "Пока нет данных по активности.",
        },
        "audience": {
            "title": "<b>Инсайты по аудитории для {title}</b>",
            "sources": "<b>Топ инвайтеров:</b>",
            "no_sources": "Нет данных по инвайтам.",
            "leavers": "<b>Чаще всего уходят:</b>",
            "no_leavers": "Нет отписок.",
            "returnees": "<b>Возвращенцы:</b>",
            "no_returnees": "Пока нет возвращенцев.",
            "ghosts": "<b>Неактивные 30+ дней:</b>",
            "no_ghosts": "Нет неактивных участников.",
        },
    },
        "alerts": {
        "mass_leave": "\u26a0\ufe0f Массовые отписки в <b>{title}</b>: {count} за последние {minutes} мин",
        "anomaly_spike": "\u26a0\ufe0f Всплеск активности в <b>{title}</b>: {count} событий за час",
        "anomaly_drop": "\u26a0\ufe0f Резкое падение активности в <b>{title}</b>",
        "milestone": "\ud83c\udf89 Новый рубеж в <b>{title}</b>: {milestone} участников!",
        "churn_threshold": "\u26a0\ufe0f Отток в <b>{title}</b>: {churn} (порог {threshold})",
        "vip_left": "\ud83d\udd25 VIP покинул <b>{title}</b> (ID {user_id})",
        "digest_daily_prefix": "\ud83d\udcc5 Дневной дайджест",
        "digest_weekly_prefix": "\ud83d\udcca Недельный дайджест",
        "digest_monthly_prefix": "\ud83d\udccb Месячный дайджест",
        "settings": {
            "title": "<b>Настройки алёртов для {title}</b>",
            "mass_leave": "Массовые отписки: {count} за {minutes} мин",
            "anomaly": "Фактор аномалий: {factor}x",
            "milestone": "Шаг мильстоуна: {step} (посл. {last})",
            "churn": "Порог оттока: {threshold}",
            "daily": "Дневной дайджест: {state}",
            "weekly": "Недельный дайджест: {state}",
            "monthly": "Месячный дайджест: {state}",
            "quiet": "Тихий режим: {quiet}",
            "quiet_off": "выключен",
            "vips": "VIP ID: {vips}",
            "vips_none": "нет",
            "clear_vips_btn": "Сбросить VIP",
            "updated": "Настройки обновлены",
            "no_channels": "У вас пока нет каналов.",
            "select_channel": "Выберите канал для настройки алёртов:",
            "channel_not_found": "Канал не найден",
            "vip_usage": "Используйте: /vip_add <id1> <id2> ...",
            "vips_set": "VIP-список обновлён: {vips}",
            "vips_cleared": "VIP-список очищен",
            "on": "ВКЛ",
            "off": "ВЫКЛ",
        },
    },
}
