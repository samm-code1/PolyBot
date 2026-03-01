# ⚙️ BOT DEVELOPMENT WORKFLOW & AI PROTOCOL

AI Assistants (Gemini, Claude, Cursor) must adhere to this workflow when generating code.

## 1. Planning Mode First
Before writing code for a new strategy or API integration, the AI must output an **Implementation Plan**.
- Reference the specific Polymarket API docs (e.g., "Using `get-order-scoring-status.md`").
- Wait for my approval before generating the code.

## 2. "Senior Dev" Troubleshooting
If we encounter a 429 Rate Limit, a CLOB API Error, or a WebSocket disconnect:
- Do not guess. Check the `Polymarket Docs Cheatsheet` (specifically `error-codes.md` and `rate-limits.md`).
- Implement exponential backoff for rate limits.
- Implement auto-reconnect logic for WebSockets.

## 3. Strict Python Rules
- ALWAYS use Type Hints (`def execute_trade(market_id: str, size: float) -> bool:`).
- Keep functions pure where possible. 
- Use Python's `logging` module (INFO for trades, DEBUG for websocket ticks, ERROR for API failures). Do not use `print()`.