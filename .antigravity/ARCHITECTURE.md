# 🏛 ARCHITECTURE: Polymarket Arbitrage Bot

## 1. Project Overview
A high-frequency, event-driven trading bot for Polymarket. 
Goal: Start with $10, run aggressive/edgy arbitrage strategies to compound up to $1000/week, trigger an automatic withdrawal of $900 to a safety net, and restart with $100. Stop-losses are mandatory.

## 2. Tech Stack & Libraries
- **Language:** Python 3.11+
- **Core SDK:** `py_clob_client` (Official Polymarket CLOB client)
- **Concurrency:** `asyncio` (Crucial for competitive edge/speed)
- **Real-time Data:** `websockets` (Consuming Market Channel & User Channel)
- **Web3/Blockchain:** `web3.py` (For L1 wallet signing, Gasless txs, and CTF Token merges/splits)
- **Environment Management:** `python-dotenv` (NEVER hardcode private keys)

## 3. Directory Structure
```text
/bot
  ├── /api          # Polymarket CLOB & L1/L2 wrappers (Authentication, Orders)
  ├── /data         # WebSocket listeners (Orderbook streaming, Midpoint prices)
  ├── /strategies   # Arbitrage logic (Negative Risk, Spread Sniping, Maker Rebates)
  ├── /risk         # Stop-loss enforcement, sizing, $1000 auto-withdraw logic
  ├── /utils        # Logging, heartbeat signals, math helpers
  ├── main.py       # Async event loop entry point