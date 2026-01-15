# Channel Analytics Bot

Telegram bot for tracking channel subscriber activity. Get instant notifications when someone subscribes or unsubscribes from your channel.

## Features

- **Real-time notifications** about subscriber changes
- **Unsubscribe tracking** - see who left your channel (main feature!)
- **Subscribe tracking** - new member notifications
- **Kick/Ban tracking** - moderation events
- **Statistics** - view channel analytics
- **CSV export** - export events data
- **Multi-channel support** - manage multiple channels

## Quick Start

### 1. Create a bot

1. Open [@BotFather](https://t.me/BotFather) in Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token

### 2. Configure environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your bot token
BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/channel_analytics_bot
ADMIN_IDS=your_telegram_id
```

### 3. Run with Docker (recommended)

```bash
# Start database and bot
docker-compose up -d

# View logs
docker-compose logs -f bot
```

### 4. Or run locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL (separately)
docker-compose up -d db

# Apply migrations
alembic upgrade head

# Run bot
python -m bot
```

## Setup Channel Tracking

1. Add the bot to your channel as **administrator**
2. Grant permission: **"Add subscribers"** (required to see member changes)
3. Bot will automatically register the channel
4. Notifications will be sent to your private chat with the bot

### Change notification destination

Use `/setchat` command in any chat (private or group) to receive notifications there.

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and channel list |
| `/stats` | View channel statistics |
| `/recent` | Recent member events |
| `/left` | Who left the channel recently |
| `/export` | Export events to CSV |
| `/setchat` | Set notification destination |
| `/help` | Help message |

## Project Structure

```
test_chanel_check_tgbot/
├── bot/
│   ├── __main__.py          # Entry point
│   ├── config.py            # Configuration
│   ├── loader.py            # Bot initialization
│   ├── handlers/
│   │   ├── channel_events.py  # Member tracking (core!)
│   │   ├── admin.py           # Bot commands
│   │   └── messages.py        # Comment tracking
│   ├── middlewares/
│   │   └── database.py        # DB session middleware
│   ├── services/
│   │   ├── notifications.py   # Alert service
│   │   └── analytics.py       # Stats service
│   └── utils/
│       └── formatting.py      # Message formatting
├── database/
│   ├── engine.py              # Async SQLAlchemy
│   ├── models/                # Database models
│   └── repositories/          # Data access layer
├── alembic/                   # Database migrations
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Tech Stack

- **Python 3.11+**
- **aiogram 3.x** - Modern async Telegram Bot API framework
- **SQLAlchemy 2.0** - Async ORM
- **PostgreSQL** - Database
- **Alembic** - Database migrations
- **Docker** - Containerization
- **Loguru** - Logging

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | required |
| `DATABASE_URL` | PostgreSQL connection string | localhost |
| `ADMIN_IDS` | Comma-separated admin user IDs | - |
| `LOG_LEVEL` | Logging level | INFO |

## Development

```bash
# Run database only
docker-compose up -d db

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## How It Works

The bot uses Telegram's `ChatMemberUpdated` event to track all member changes in channels where it's added as administrator. When someone joins or leaves:

1. Telegram sends `chat_member` update to the bot
2. Bot saves event to database
3. Bot sends notification to configured chat
4. Statistics are updated

## License

MIT
