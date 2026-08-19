# Project

Telegram-to-MT5 signal middleware.

## Current scope

Telegram signal groups
→ message ingestion
→ analysis and parsing
→ normalization
→ validation
→ MT5 bridge API

The MT5 EA is outside this repository and owns trade execution and trade-management logic.

cTrader is currently out of scope.

## Tech stack

- Python 3.13
- uv
- Telethon
- Pydantic
- Pydantic Settings
- FastAPI
- Uvicorn
- Ruff
- pytest

## Dependency management

Use uv only.

Do not use pip directly.

Runtime dependency:

uv add <package>

Development dependency:

uv add --dev <package>

## Required checks

Before completing code changes:

uv run ruff check .
uv run ruff format --check .
uv run pytest

## Secrets

Do not attempt to read, print, inspect, copy, modify, or expose:

- `.env`
- `*.session`
- `*.session-journal`
- Telegram credentials
- MT5 credentials
- API tokens

Use `.env.example` to understand available configuration keys.

## Architecture

Telegram messages must never directly trigger an MT5 order.

Messages pass through:

ingestion
→ parsing
→ normalization
→ validation
→ outbox
→ MT5 API
