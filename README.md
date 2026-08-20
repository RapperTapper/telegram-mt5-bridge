# Telegram MT5 Bridge

Telegram-to-MT5 middleware that currently collects raw Telegram messages in a local SQLite
database. Parsing, normalization, validation, and the MT5 bridge API follow in later phases.
Trade execution and trade management remain inside the MT5 EA.

New to the project? Follow the detailed German beginner guide:
[SETUP.md](SETUP.md).

## First-time setup

### 1. Install uv

On macOS with Homebrew:

```console
brew install uv
```

Alternatively, use the
[official installation instructions](https://docs.astral.sh/uv/getting-started/installation/).

### 2. Install the project

```console
git clone https://github.com/RapperTapper/telegram-mt5-bridge.git
cd telegram-mt5-bridge
uv sync --locked
```

### 3. Configure Telegram credentials

Create the local configuration file:

```console
cp .env.example .env
```

Open `.env` in an editor and set:

```dotenv
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=your-api-hash
```

Create your own Telegram API credentials at <https://my.telegram.org>. Never commit `.env` or
share its contents.

### 4. Authenticate Telegram

```console
uv run telegram-mt5-auth
```

Complete Telegram's interactive login once. The local Telethon session is reused on later runs.

### 5. Find and allow chats

List the chats available to the authenticated Telegram account:

```console
uv run telegram-mt5-dialogs
```

Add the desired IDs to `.env` as a comma-separated allowlist:

```dotenv
TELEGRAM_ALLOWED_CHAT_IDS=-100123456789,-100987654321
```

Negative IDs are normal for Telegram groups and channels. Chat names are printed only by the
dialog command and are not written to the collector logs.

### 6. Check the local setup

```console
uv run telegram-mt5-doctor
```

The Doctor checks local configuration, the Telegram session, runtime directories, SQLite access,
and aggregate database statistics. It does not connect to Telegram and does not display secrets or
message contents.

### 7. Start collecting

```console
uv run telegram-mt5-collect
```

Keep the process running and press `Ctrl+C` to stop it. The collector stores new messages, edits,
and observed deletions from allowlisted chats. It never places an MT5 order.

### 8. Check collected data

```console
uv run telegram-mt5-db-stats
```

This shows aggregate event, feature, and per-chat counts without exposing message text.

## Commands

| Command | Purpose |
| --- | --- |
| `uv run telegram-mt5-auth` | Authenticate the Telegram account once |
| `uv run telegram-mt5-dialogs` | List available Telegram chat IDs and names |
| `uv run telegram-mt5-doctor` | Diagnose the local setup without connecting to Telegram |
| `uv run telegram-mt5-collect` | Run the raw Telegram message collector |
| `uv run telegram-mt5-db-stats` | Show aggregate SQLite collection statistics |

## Runtime data

Runtime data is stored outside the repository in the platform-specific application data directory:

- macOS: `~/Library/Application Support/TelegramMT5Bridge`
- Windows: `%LOCALAPPDATA%\TelegramMT5Bridge`
- Linux: `~/.local/share/TelegramMT5Bridge`

The SQLite database is stored below that directory as `runtime/messages.sqlite3`.

## Architecture and scope

```text
Telegram groups and channels
        ↓
message ingestion and raw SQLite snapshots
        ↓
parsing
        ↓
normalization
        ↓
validation
        ↓
outbox
        ↓
MT5 bridge API
```

Telegram messages never directly trigger MT5 orders. The external MT5 EA owns trade execution and
trade-management logic. cTrader is currently out of scope.

## Development checks

```console
uv run ruff check .
uv run ruff format --check .
uv run pytest
```
