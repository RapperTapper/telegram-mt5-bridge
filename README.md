# Telegram MT5 Bridge

Middleware for ingesting Telegram trading signals, analyzing and normalizing them, and exposing validated signals to an MT5 Bridge EA.

## Current scope

Telegram
→ message ingestion
→ analysis/parsing
→ normalization
→ validation
→ MT5 bridge API

Trade execution and trade-management logic remain inside the MT5 EA.
